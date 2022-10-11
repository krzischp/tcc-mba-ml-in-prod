FROM python:3.7-slim

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . .

COPY /requirements.txt /tmp/requirements.txt
RUN apt-get update -yqq && \
    apt-get -yqq install libsndfile1 --no-install-recommends && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --compile -r /tmp/requirements.txt && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/* /tmp/* /var/tmp/*

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app
