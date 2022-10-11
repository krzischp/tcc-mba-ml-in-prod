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

ENTRYPOINT ./cloud_sql_proxy -instances=${INSTANCE_CONNECTION_NAME}=tcp:3306 -credential_file=${GOOGLE_APPLICATION_CREDENTIALS} && mlflow server -h 0.0.0.0 -p 5000 --default-artifact-root ${MLFLOW_ARTIFACT_URL} --backend-store-uri ${MLFLOW_DATABASE_URL}