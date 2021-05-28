## DAG Loading

This is a manual process to load a DAG.


```bash
# Setup Variables
UNIQUE="<your_osdu_unique>"         # ie: demo
AZURE_DNS_NAME="<your_osdu_fqdn>"   # ie: osdu-$UNIQUE.contoso.com
DATA_PARTITION="<your_partition>"   # ie:opendes
ACR_REGISTRY="<your_acr_fqdn>"      # ie: msosdu.azurecr.io


DAG_TASK_IMAGE="$ACR_REGISTRY/vds_dag"
DAG_LOAD_IMAGE="$ACR_REGISTRY/segy-to-vds-conversion-dag"
TAG="latest"

# This logs your local Azure CLI in using the configured service principal.
az login --service-principal -u $ARM_CLIENT_ID -p $ARM_CLIENT_SECRET --tenant $ARM_TENANT_ID

GROUP=$(az group list --query "[?contains(name, 'cr${UNIQUE}')].name" -otsv)
ENV_VAULT=$(az keyvault list --resource-group $GROUP --query [].name -otsv)

cat > .env << EOF
DAG_TASK_IMAGE=$DAG_TASK_IMAGE:$TAG
SHARED_TENANT=$SHARED_TENANT
AZURE_TENANT_ID=$AZURE_TENANT_ID
AZURE_DNS_NAME=$AZURE_DNS_NAME
AZURE_AD_APP_RESOURCE_ID=$AZURE_AD_APP_RESOURCE_ID
AZURE_CLIENT_ID=$AZURE_CLIENT_ID
AZURE_CLIENT_SECRET=$AZURE_CLIENT_SECRET
EOF

(cd ../../.. && docker build -f deployments/scripts/azure/Dockerfile -t $DAG_LOAD_IMAGE:$TAG .)
docker run --env-file .env $DAG_LOAD_IMAGE:$TAG
```
