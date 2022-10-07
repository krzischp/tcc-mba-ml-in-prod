FROM pytorch/pytorch:1.9.0-cuda10.2-cudnn7-runtime

USER root
RUN apt-get update && apt-get install -y libsm6 libxrender1 libfontconfig1 libxext6 libglib2.0-0 gcc binutils less git

ENV APP_DIR='/workers'
COPY /tcc-lucas-pierre-7490c66905ca.json $APP_DIR/tcc-lucas-pierre-7490c66905ca.json
ENV GOOGLE_APPLICATION_CREDENTIALS=$APP_DIR/tcc-lucas-pierre-7490c66905ca.json
WORKDIR $APP_DIR

COPY /requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --compile -r /tmp/requirements.txt && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/* /tmp/* /var/tmp/*
RUN pip install -U typing_extensions

ADD utils $APP_DIR/utils
ADD deepfashion.py $APP_DIR/
ADD main.py $APP_DIR/

CMD exec gunicorn --preload --bind :$PORT --workers 1 --threads 8 main:app
