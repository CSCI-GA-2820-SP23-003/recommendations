#!/bin/bash
#set -x

echo "*********************  DELETE SERVICE ***********************"

kubectl delete deployment.apps/nyu-devops-recommendation
kubectl delete service/nyu-devops-recommendation

echo ""
echo "************************************************************"
echo "What's running now..."
kubectl get all
echo ""