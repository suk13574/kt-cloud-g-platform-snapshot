FROM python:3.12

WORKDIR /app

COPY . /app

COPY src/config/config.yml /app/src/config/

COPY disk_snapshot_list /etc/snapshot/config

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

CMD ["python", "src/main.py"]