#!/bin/bash
#set -x

echo "*********************  BEGIN DEPLOY  ***********************"
SPACE=dev
NODE_PORT=31001
PIPELINE_IMAGE_URL=us.icr.io/yjlo/nyu-devops-recommendation:1.0

# Install latest yq because the cloud version is back leveled 
# wget -qO yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
# chmod +x yq

echo "Deploying image: $PIPELINE_IMAGE_URL to: $SPACE on NodePort: $NODE_PORT..."
kubectl config set-context --current --namespace $SPACE

echo ""
echo "*********************  DEPLOYMENT  ***********************"
echo ""
# cat deploy/deployment.yaml | ./yq eval ".spec.template.spec.containers[0].image = \"$PIPELINE_IMAGE_URL\"" > deployment.yaml
# cat deployment.yaml
kubectl apply -f deploy/deployment.yaml

echo ""
echo "***********************  SERVICE  **************************"
echo ""

# cat deploy/service.yaml | ./yq eval ".spec.ports[0].nodePort = $NODE_PORT" > service.yaml
# cat service.yaml
kubectl apply -f deploy/service.yaml

echo ""
echo "************************************************************"
echo "What's running now..."
kubectl get all
echo ""