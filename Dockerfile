FROM python:3.13-bookworm

COPY requirements.txt /requirements.txt

RUN python3.13 -m pip install --no-cache-dir -r /requirements.txt

COPY start.sh /start.sh

RUN chmod -x /start.sh

COPY app /app

RUN mkdir /data \
    && chmod -R 666 /data

COPY src /src

CMD ["sh", "/start.sh"]
