FROM python:3.8-slim

COPY /requirements.txt /tmp/requirements.txt
ENV APP_DIR='/workers'
COPY /tcc-lucas-pierre-7490c66905ca.json $APP_DIR/tcc-lucas-pierre-7490c66905ca.json
ENV GOOGLE_APPLICATION_CREDENTIALS=$APP_DIR/tcc-lucas-pierre-7490c66905ca.json
WORKDIR $APP_DIR

RUN apt-get update -yqq && \
    apt-get -yqq install libsndfile1 --no-install-recommends && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --compile -r /tmp/requirements.txt && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/* /tmp/* /var/tmp/*

ADD /app $APP_DIR/app/
ADD worker.py $APP_DIR/
EXPOSE 6379 5672