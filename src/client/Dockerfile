FROM jupyter/base-notebook:latest

COPY /requirements.txt /tmp/requirements.txt
COPY /tcc-lucas-pierre-7490c66905ca.json /tmp/tcc-lucas-pierre-7490c66905ca.json
ENV GOOGLE_APPLICATION_CREDENTIALS=/tmp/tcc-lucas-pierre-7490c66905ca.json

# ADDING for testing in Kubernetes
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --compile -r /tmp/requirements.txt

USER root
# RUN chmod -R 777 /home/jovyan
# mounted notebooks folder doesn't exist yet in Kubernetes because it is a VolumeClaim
# it only exists on local with docker-compose.yaml as an existing volume is mounted before Dockerfile execution
COPY notebooks/client.ipynb /home/jovyan/eda.ipynb
# RUN chown -R ${NB_UID}:${NB_GID} /home/jovyan
RUN chown ${NB_UID}:${NB_GID} /home/jovyan/eda.ipynb
USER ${NB_UID}
