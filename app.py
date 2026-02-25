#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime, timedelta

import requests

def get_env():
    token = os.environ.get("CF_API_TOKEN")
    if not token:
        print("Missing required environment variable: CF_API_TOKEN", file=sys.stderr)
        sys.exit(1)

    records = []
    i = 0
    while True:
        val = os.environ.get(f"DNS_RECORD_{i}")
        if val is None:
            break
        parts = val.split(":")
        if len(parts) != 3 or not all(parts):
            print(f"Invalid format for DNS_RECORD_{i}: expected 'zone_id:record_id:name'", file=sys.stderr)
            sys.exit(1)
        records.append({"zone_id": parts[0], "record_id": parts[1], "name": parts[2]})
        i += 1

    if not records:
        print("No DNS records defined. Set DNS_RECORD_0=zone_id:record_id:name, DNS_RECORD_1=..., etc.", file=sys.stderr)
        sys.exit(1)

    return {
        "cf_api_token": token,
        "records": records,
        "interval": int(os.environ.get("INTERVAL", "300")),
    }

def get_public_ip():
    resp = requests.get("https://api.ipify.org", timeout=10)
    resp.raise_for_status()
    return resp.text.strip()

def get_dns_ip(token, zone_id, record_id):
    resp = requests.get(
        f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["result"]["content"]

def update_dns(token, zone_id, record_id, name, ip, interval):
    now = datetime.now()
    next_check = now + timedelta(seconds=interval)
    comment = (
        f"Automatically edited by cfddns worker. "
        f"Update: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    resp = requests.put(
        f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={
            "type": "A",
            "name": name,
            "content": ip,
            "ttl": 120,
            "comment": comment,
            "proxied": True,
        },
        timeout=10,
    )

    resp.raise_for_status()
    return resp.json()

def main():
    cfg = get_env()
    token = cfg["cf_api_token"]
    records = cfg["records"]
    interval = cfg["interval"]

    record_names = ", ".join(r["name"] for r in records)
    print(f"Starting cfddns | records: {record_names} | interval: {interval}s")

    while True:
        try:
            current_ip = get_public_ip()
        except Exception as e:
            print(f"Failed to get public IP: {e}")
            time.sleep(interval)
            continue

        now = datetime.now().isoformat(timespec="seconds")
        for record in records:
            zone_id = record["zone_id"]
            record_id = record["record_id"]
            name = record["name"]

            try:
                dns_ip = get_dns_ip(token, zone_id, record_id)
            except Exception as e:
                print(f"{now} [{name}] Failed to query Cloudflare: {e}")
                continue

            if current_ip == dns_ip:
                print(f"{now} [{name}] IP unchanged: {current_ip}")
            else:
                print(f"{now} [{name}] Updating IP from {dns_ip} to {current_ip}")
                try:
                    update_dns(token, zone_id, record_id, name, current_ip, interval)
                except Exception as e:
                    print(f"{now} [{name}] Failed to update DNS: {e}")

        time.sleep(interval)

if __name__ == "__main__":
    main()
