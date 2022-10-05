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
# first drag and drop the files in k8s from your local to Google Cloud editor's file system
# then execute the following command line in Google Cloud editor:
kubectl apply -f api-deployment.yaml,api-service.yaml,backend-deployment.yaml,backend-service.yaml,broker-deployment.yaml,broker-service.yaml,client-claim0-persistentvolumeclaim.yaml,client-deployment.yaml,client-service.yaml,database-claim0-persistentvolumeclaim.yaml,database-deployment.yaml,database-service.yaml,imagery-worker-deployment.yaml,inference-worker-deployment.yaml,network-networkpolicy.yaml,variables-env-configmap.yaml
# if you need to delete created resources:
kubectl delete -f api-deployment.yaml,api-service.yaml,backend-deployment.yaml,backend-service.yaml,broker-deployment.yaml,broker-service.yaml,client-claim0-persistentvolumeclaim.yaml,client-deployment.yaml,client-service.yaml,database-claim0-persistentvolumeclaim.yaml,database-deployment.yaml,database-service.yaml,imagery-worker-deployment.yaml,inference-worker-deployment.yaml,network-networkpolicy.yaml,variables-env-configmap.yaml

##################### util command lines
# push to Google Container Registry
gcloud services enable containerregistry.googleapis.com
gcloud auth login

# (--pull so we always attempt to pull a newer version of the image)
docker-compose build --pull
docker-compose push

# or same thing for one image only:
docker build -t gcr.io/tcc-lucas-pierre/client .
docker build -t gcr.io/tcc-lucas-pierre/imagery_worker .
docker-compose build imagery_worker
docker-compose up
docker run -it -p 8888:8888 gcr.io/tcc-lucas-pierre/client

docker push gcr.io/tcc-lucas-pierre/client

### Expose the Deployment
You need to expose it to the internet so that users can access it. You can expose your application by creating a Service, a Kubernetes resource that exposes your application to external traffic:
kubectl expose deployment client \
--type LoadBalancer \
--port 80 \
--target-port 8888

- Passing in the --type LoadBalancer flag creates a Compute Engine load balancer for your container. 
- The --port flag initializes public port 80 to the internet 
- and the --target-port flag routes the traffic to port 8080 of the application


# check created objects
kubectl get nodes -A
kubectl get deployments
kubectl get services
kubectl get service my-cip-service --output yaml
kubectl get pod -n default

kubectl describe pod -n default client-7d6bc5485f-vlrhq
kubectl logs client-5f594f7c94-jppvs

kubectl delete -f tcc-mba-ml-in-prod/client-deployment.yaml
kubectl apply -f tcc-mba-ml-in-prod/client-deployment.yaml


# Get a shell into one of your running containers:
kubectl exec -it client-5d8fc778bd-29vg8 -- sh
# then install curl to send request to your service:
apk add --no-cache curl
curl CLUSTER_IP:80


# when exposing a pod with a LoadBalancer, use this command line to view the external IP and exposed PORT
# obs: you cannot access it if it is in a specific network
# worst case: we could try with no network policy at all, and look at this later
kubectl get services | grep client
NAME           TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)             AGE
client-mcskw   LoadBalancer   10.83.128.109   34.139.26.116   80:30905/TCP        5m37s
We can then access 34.139.26.116:80 in this case.
