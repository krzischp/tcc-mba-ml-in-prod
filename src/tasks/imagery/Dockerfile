FROM python:3.7-slim

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY /tcc-lucas-pierre-7490c66905ca.json $APP_HOME/tcc-lucas-pierre-7490c66905ca.json
ENV GOOGLE_APPLICATION_CREDENTIALS=$APP_HOME/tcc-lucas-pierre-7490c66905ca.json
COPY . .

RUN pip install Flask gunicorn
RUN apt-get update -yqq && \
    apt-get -yqq install libsndfile1 --no-install-recommends && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --compile -r /tmp/requirements.txt && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/* /tmp/* /var/tmp/*

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app
