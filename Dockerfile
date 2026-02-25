FROM python:3.13-alpine

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /usr/local/bin/app.py

ENTRYPOINT ["python", "/usr/local/bin/app.py"]
