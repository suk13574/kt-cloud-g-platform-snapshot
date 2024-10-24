FROM python:3.12

WORKDIR /app

COPY . /app

RUN mkdir -p /etc/snapshot/config

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

ENV TZ Asia/Seoul

CMD ["python", "src/main.py"]