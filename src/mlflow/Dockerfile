FROM python:3.9-slim-buster
WORKDIR /usr/src/app

COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
ENV MLFLOW_ARTIFACT_URL ${MLFLOW_ARTIFACT_URL}
ENV MLFLOW_USER ${MLFLOW_USER}
ENV MLFLOW_PASSWORD ${MLFLOW_PASSWORD}
RUN apt update && apt install -y wget
RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.386 -O cloud_sql_proxy
RUN chmod +x cloud_sql_proxy
RUN chmod +x init.sh

ENTRYPOINT ["bash", "./init.sh"]