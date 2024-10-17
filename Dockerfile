FROM python:3.12

WORKDIR /app

COPY . /app

COPY disk_snapshot_list /etc/snapshot/config

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "src/main.py"]