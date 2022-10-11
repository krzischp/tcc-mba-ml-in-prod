FROM python:3.7-slim

COPY /requirements.txt /api/requirements.txt

ENV APP_DIR='/api'
WORKDIR $APP_DIR

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --compile -r requirements.txt && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/* /tmp/* /var/tmp/*

ADD /tests $APP_DIR/tests/
ADD main.py $APP_DIR/

CMD uvicorn main:app --host 0.0.0.0 --port 5000