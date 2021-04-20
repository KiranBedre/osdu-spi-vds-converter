## DAG Loading

This is a manual process to load a DAG.


```bash
# Setup Variables
UNIQUE="<your_osdu_unique>"         # ie: demo
AZURE_DNS_NAME="<your_osdu_fqdn>"   # ie: osdu-$UNIQUE.contoso.com
DATA_PARTITION="<your_partition>"   # ie:opendes
ACR_REGISTRY="<your_acr_fqdn>"      # ie: myacr.azurecr.io

DAG_TAG=="$ACR_REGISTRY/vds_dag"
TAG="latest"

# This logs your local Azure CLI in using the configured service principal.
az login --service-principal -u $ARM_CLIENT_ID -p $ARM_CLIENT_SECRET --tenant $ARM_TENANT_ID

GROUP=$(az group list --query "[?contains(name, 'cr${UNIQUE}')].name" -otsv)
ENV_VAULT=$(az keyvault list --resource-group $GROUP --query [].name -otsv)

cat > .env << EOF
DAG_IMAGE=${AZURE_REGISTRY}.azurecr.io/$DAG_TAG
SHARED_TENANT=$SHARED_TENANT
AZURE_TENANT_ID=$AZURE_TENANT_ID
AZURE_DNS_NAME=$AZURE_DNS_NAME
AZURE_AD_APP_RESOURCE_ID=$AZURE_AD_APP_RESOURCE_ID
AZURE_CLIENT_ID=$AZURE_CLIENT_ID
AZURE_CLIENT_SECRET=$AZURE_CLIENT_SECRET
EOF

(cd ../../.. && docker build -f deployments/scripts/azure/Dockerfile -t $ACR_REGISTRY/$DAG_IMAGE:$TAG .)
docker run -it --env-file .env $ACR_REGISTRY/$DAG_IMAGE:$TAG
```