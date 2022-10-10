# Youtube video tutorial
Um video foi gravado para explicar como rodar e usar o projeto.

No vídeo, vocês devem explicar o processo do machine learning que vocês desenvolveram, 
- desde a fonte dos dados, 
- passando pela preparação, 
- processamento, 
- chegando ao modelo e à escala do modelo.


## Cluster no Kubernetes
### Criar o cluster no Kubernetes
```sh
gcloud config set project tcc-lucas-pierre
gcloud compute zones list | grep us-east1
gcloud config set compute/region us-east1

gcloud container clusters create tcc-cluster --project=tcc-lucas-pierre --region=us-east1 --num-nodes=2 --preemptible

gcloud container clusters get-credentials tcc-cluster --region us-east1
```

### Remover o cluster no Kubernetes
```sh
gcloud container clusters delete --region=us-east1 tcc-cluster
```

## Filas no Cloud Task
### Criar as filas no Cloud Task
```sh
cd src/tasks/imagery
gcloud app deploy
```

```sh
cd src/tasks/inference
gcloud app deploy
```

### Debogar as filas
```sh
gcloud app logs tail -s imagery
gcloud app logs tail -s inference
```

## Passo a passo no local
```sh
make build
```

```sh
make up
```

## Passo a passo na Kubernetes
### Executar os deployments
```sh
kubectl apply -f api-deployment.yaml,client-claim0-persistentvolumeclaim.yaml,client-service.yaml,variables-env-configmap.yaml,api-service.yaml,client-deployment.yaml,network-networkpolicy.yaml
```

### Checar os status dos deployments
kubectl get deployments

### Acessar o serviço client
```sh
kubectl get services | grep client
```
