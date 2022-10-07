FROM jupyter/base-notebook:latest

COPY /requirements.txt /tmp/requirements.txt
COPY /tcc-lucas-pierre-7490c66905ca.json /tmp/tcc-lucas-pierre-7490c66905ca.json
ENV GOOGLE_APPLICATION_CREDENTIALS=/tmp/tcc-lucas-pierre-7490c66905ca.json

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --compile -r /tmp/requirements.txt

USER root
COPY notebooks/client.ipynb /home/jovyan/client.ipynb
RUN chown ${NB_UID}:${NB_GID} /home/jovyan/client.ipynb
USER ${NB_UID}
