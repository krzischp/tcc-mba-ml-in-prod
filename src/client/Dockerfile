FROM jupyter/base-notebook:latest

COPY /requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --compile -r /tmp/requirements.txt

USER root
COPY notebooks/client.ipynb /home/jovyan/client.ipynb
RUN chown ${NB_UID}:${NB_GID} /home/jovyan/client.ipynb
USER ${NB_UID}
