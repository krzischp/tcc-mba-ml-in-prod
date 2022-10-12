#!/bin/bash
export INSTANCE_CONNECTION_NAME="tcc-lucas-pierre:southamerica-east1:mlflow"
./cloud_sql_proxy -instances="${INSTANCE_CONNECTION_NAME}"=tcp:0.0.0.0:3306 -credential_file="${GOOGLE_APPLICATION_CREDENTIALS}" &
mlflow server -h 0.0.0.0 -p 5000 --default-artifact-root "${MLFLOW_ARTIFACT_URL}" --backend-store-uri "${MLFLOW_DATABASE_URL}"