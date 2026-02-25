# Cloudflare Dynamic DNS Updater

A lightweight Python background service that keeps your Cloudflare DNS A records in sync with your current public IP address. Useful for home servers or any environment with a dynamic IP.

## How it works

1. Fetches your current public IP from [api.ipify.org](https://api.ipify.org)
2. Compares it against each configured Cloudflare DNS record
3. Updates only the records whose IP has changed
4. Repeats on a configurable interval (default: 5 minutes)

Records are set as **proxied**, **TTL 120**, and tagged with an automated comment on each update.

---

## Prerequisites

- A Cloudflare account with your domain added
- A Cloudflare API token with **DNS Edit** permissions (see [below](#cloudflare-api-token))
- The **Zone ID** and **Record ID** for each DNS record you want to manage (see [below](#finding-zone-id-and-record-id))

---

## Configuration

All configuration is done via environment variables.

| Variable | Required | Default | Description |
|---|---|---|---|
| `CF_API_TOKEN` | Yes | — | Cloudflare API token with DNS edit permissions |
| `DNS_RECORD_0` | Yes | — | First DNS record in `zone_id:record_id:name` format |
| `DNS_RECORD_1` | No | — | Additional records follow the same format |
| `DNS_RECORD_N` | No | — | Add as many as needed (sequential, starting from 0) |
| `INTERVAL` | No | `300` | How often to check for IP changes, in seconds |

### DNS record format

```
DNS_RECORD_0=<zone_id>:<record_id>:<record_name>
```

Example:
```
DNS_RECORD_0=abc123def456:xyz789:home.example.com
DNS_RECORD_1=abc123def456:uvw012:vpn.example.com
```

---

## Usage

### Docker Compose (recommended)

Copy the example below into a `docker-compose.yml` and fill in your values:

```yaml
services:
  cloudflare-dns-updater:
    image: ghcr.io/idohomri-io/cloudflare-dns-updater:latest
    container_name: cloudflare-dns-updater
    restart: unless-stopped
    environment:
      - CF_API_TOKEN=your_api_token_here
      - DNS_RECORD_0=zone_id:record_id:home.example.com
      # - DNS_RECORD_1=zone_id:record_id:vpn.example.com
      - INTERVAL=300
```

```bash
docker compose up -d
```

### Docker

```bash
docker run -d \
  --name cloudflare-dns-updater \
  --restart unless-stopped \
  -e CF_API_TOKEN=your_api_token_here \
  -e DNS_RECORD_0=zone_id:record_id:home.example.com \
  -e INTERVAL=300 \
  ghcr.io/idohomri-io/cloudflare-dns-updater:latest
```

### Python (without Docker)

```bash
pip install requests

CF_API_TOKEN=your_token \
DNS_RECORD_0=zone_id:record_id:home.example.com \
python app.py
```

---

## Cloudflare API Token

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com) → **My Profile** → **API Tokens**
2. Click **Create Token** → use the **Edit zone DNS** template
3. Under **Zone Resources**, select the specific zone(s) you want to manage
4. Create the token and copy it — it won't be shown again

> The token only needs `Zone → DNS → Edit` permission. No other permissions are required.

---

## Finding Zone ID and Record ID

### Zone ID

1. Go to your domain in the Cloudflare Dashboard
2. Scroll down on the **Overview** tab
3. Copy the **Zone ID** from the right-hand panel

### Record ID

Use the Cloudflare API to list your DNS records and find the record ID:

```bash
curl -X GET "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/dns_records?type=A" \
  -H "Authorization: Bearer <CF_API_TOKEN>" \
  -H "Content-Type: application/json"
```

Look for `"id"` in the response for the record you want to manage.

---

## Logs

The service logs to stdout. Each check produces a line per record:

```
2026-02-25T10:00:00 [home.example.com] IP unchanged: 1.2.3.4
2026-02-25T10:05:00 [home.example.com] Updating IP from 1.2.3.4 to 5.6.7.8
```

View live logs with Docker:

```bash
docker logs -f cloudflare-dns-updater
```

---

## Building from source

```bash
docker build --platform linux/amd64 -t cloudflare-dns-updater .
```
