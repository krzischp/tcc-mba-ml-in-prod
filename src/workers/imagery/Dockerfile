FROM python:3.7-slim

COPY /requirements.txt /tmp/requirements.txt

ENV APP_DIR='/workers'
WORKDIR $APP_DIR

RUN apt-get update -yqq && \
    apt-get -yqq install libsndfile1 --no-install-recommends && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --compile -r /tmp/requirements.txt && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/* /tmp/* /var/tmp/*

ADD /app $APP_DIR/app/
ADD worker.py $APP_DIR/

EXPOSE 6379 5672