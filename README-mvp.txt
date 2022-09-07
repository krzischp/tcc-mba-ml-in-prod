##################### Cluster creation in Google Cloud
# Create the cluster - to run in Cloud Shell
gcloud config set project tcc-lucas-pierre
gcloud compute zones list | grep us-east1
gcloud config set compute/region us-east1

gcloud container clusters create-auto tcc-cluster \
    --project=tcc-lucas-pierre \
    --region=us-east1

# https://cloud.google.com/sdk/gcloud/reference/container/clusters/create-auto#--network

gcloud container clusters get-credentials tcc-cluster --region us-east1

# Create cluster without autopilot

gcloud container clusters create tcc-cluster --project=tcc-lucas-pierre --region=us-east1 --num-nodes=2 --preemptible

# to delete the cluster:
gcloud container clusters delete --region=us-east1 tcc-cluster


##################### Cluster creation in Google Cloud Editor
# first drag and drop the files in kubectl-files from your local to Google Cloud editor's file system
# then execute the following command line in Google Cloud editor:
kubectl apply -f api-deployment.yaml,api-service.yaml,backend-deployment.yaml,backend-service.yaml,broker-deployment.yaml,broker-service.yaml,database-service.yaml,client-claim0-persistentvolumeclaim.yaml,client-deployment.yaml,client-service.yaml,database-claim0-persistentvolumeclaim.yaml,database-deployment.yaml,imagery-worker-claim0-persistentvolumeclaim.yaml,imagery-worker-deployment.yaml,inference-worker-claim0-persistentvolumeclaim.yaml,inference-worker-deployment.yaml,localstack-claim0-persistentvolumeclaim.yaml,localstack-claim1-persistentvolumeclaim.yaml,localstack-deployment.yaml,network-networkpolicy.yaml,variables-env-configmap.yaml


# Current issue:
with imagery-worker-deployment

# error log:
  raise exception
File "/usr/local/lib/python3.7/site-packages/sqlalchemy/pool/base.py", line 656, in __connect
  connection = pool._invoke_creator(self)
File "/usr/local/lib/python3.7/site-packages/sqlalchemy/engine/strategies.py", line 114, in connect
  return dialect.connect(*cargs, **cparams)
File "/usr/local/lib/python3.7/site-packages/sqlalchemy/engine/default.py", line 508, in connect
  return self.dbapi.connect(*cargs, **cparams)
File "/usr/local/lib/python3.7/site-packages/psycopg2/__init__.py", line 122, in connect
  conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
