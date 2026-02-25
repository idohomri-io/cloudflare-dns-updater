FROM python:3.13-alpine

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY update-dns.py /usr/local/bin/update-dns.py

ENTRYPOINT ["python", "/usr/local/bin/update-dns.py"]
