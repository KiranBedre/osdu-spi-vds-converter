# Quick Start instructions for work with SEGY -> OpenVDS parser (Pre-ship)
- [Quick Start instructions for work with SEGY -> OpenVDS parser (Pre-ship)](#quick-start-instructions-for-work-with-segy---openvds-parser-pre-ship)
  - [Prerequisites](#prerequisites)
    - [Required Entitlements groups](#required-entitlements-groups)
    - [Generate ID token](#generate-id-token)
    - [Install SDUTIL](#install-sdutil)
    - [Other issues](#other-issues)
  - [Segy -> OpenVDS conversion](#segy---openvds-conversion)
    - [Create Seismic Store's `tenant` and `subprojects`](#create-seismic-stores-tenant-and-subprojects)
    - [Upload Segy-file from you machine USING SDUTIL](#upload-segy-file-from-you-machine-using-sdutil)
    - [Start Segy -> OpenVDS conversion workflow](#start-segy---openvds-conversion-workflow)


This guide is about how to run Segy->OpenVDS conversion Workflow on  Pre-ship.

## Prerequisites

### Required Entitlements groups

Be sure you are in the following Entitlements groups(GET: `{{entitlements_api_url}}/entitlements/v2/groups`):

- `users.datalake.admins`
- `app.trusted`
- `service.seistore.admin`
- `service.entitlements.user`
- `service.workflow.creator`
- `seistore.system.admin`


### Generate ID token

Seismic Store requires well-generated ID token.

Follow this guide to get API Credentials: https://community.opengroup.org/osdu/documentation/-/wikis/Releases/R2.0/GCP/GCP-Operation/User-Mng/OpenID-Connect#how-to-get-api-credentials-using-gcp-openid-playgroud

The most common issue with generating right ID token is using wrong **ClientID** and **ClientSecrets**. Contact our devopses to obtain the right ones.

### Install SDUTIL

SDUTIL is a command line Python utility designed to work easily with Seismic Store.

Follow the installation guide here: https://community.opengroup.org/osdu/platform/domain-data-mgmt-services/seismic/seismic-dms-suite/seismic-store-sdutil#installation

Replace the content of `seismic-store-sdutil/sdlib/config.yaml` with this:

```yaml
seistore:
  service: '{"google": {"defaultEnv":{"url": "<seismic_store_host>/api/v3", "appkey": ""}}}'
  url: '<seismic_store_host>/api/v3'
  cloud_provider: 'google'
  key: ''
  env: 'defaultEnv'
  auth-mode: 'JWT Token'
  ssl_verify: False
  APPKEY: ''
  APPKEY_NAME: ''
auth_provider:
  default: ''
gcp:
  empty: 'none'

```

Then, initialize configs:

```shell
python sdutil config init
```

And choose the first option:

```shell
[1] google

Select the cloud provider: 1
```

Then, you may skip inserting the google (defaultEnv) application key.


Now your SDUTIL is ready to use with JWT token (your ID token).

Example:


```shell
python sdutil stat sd://<your_tenant> --idtoken=$ID_token
```

### Other issues

You may find it useful to read this page: https://community.opengroup.org/osdu/documentation/-/wikis/Releases/R2.0/GCP/GCP-Pre-Prod-Onboarding-Documentation


## Segy -> OpenVDS conversion

### Create Seismic Store's `tenant` and `subprojects`

The seismic store uri is a string used to uniquely address a resource in the system and can be obtained by appending the prefix sd:// before the required resource path: `sd://<tenant>/<subproject>/<path>*/<dataset>`

Before you start uploading the file, you may create `tenant` and `subproject`.

If you want to use **already created** `tenant` and `subproject`, ask the owner (creator) of the `subroject` to add you to it:

```shell
curl --location --request PUT '<seismic_store_host>/api/v3/user' \
--header 'Authorization: Bearer <id_token>' \
--header 'Content-Type: application/json' \
--header 'x-api-key: test' \
--header 'appkey: test' \
--data-raw '{
	"email": "<your_email>@<domain>.com",
	"path": "sd://<tenant>/<subproject>",
	"group": "editor"
}'
```

This command will add you to required Entitlements groups to work with the concrete `subproject.`

Create the `tenant`:

```shell
curl --location -g --request POST '<seismic_store_host>/api/v3/tenant/<new-tenant>' \
--header 'Authorization: Bearer <id_token>' \
--header 'data-partition-id: <data-partition-id>' \
--header 'Content-Type: application/json' \
--data-raw '{
    "gcpid": "<pre-ship GCP project ID>",
    "esd": "<data-partition-id>.<domain>.com",
    "default_acl": "data.default.owners@<data-partition-id>.<domain>.com"
}'
```

Then, create the `subproject`:

```shell
curl --location -g --request POST '<seismic_store_host>/api/v3/subproject/tenant/<new-tenant>/subproject/<subproject>' \
--header 'Authorization: Bearer <id_token>' \
--header 'Content-Type: application/json' \
--header 'ltag: <data-partition-id>-demo-legaltag' \
--header 'appkey: test' \
--header 'data-partition-id: <data-partition-id>' \
--data-raw '{

    "storage_class": "MULTI_REGIONAL",
    "storage_location": "US",
    "acl": {
        "owners": [
            "data.default.owners@<data-partition-id>.<domain>.com"
        ],
        "viewers": [
            "data.default.viewers@<data-partition-id>.<domain>.com"
        ]
    }
}'
```


### Upload Segy-file from you machine using SDUTIL

After you installed SDUTIL you must have:
- all required groups in Entitlements;
- well-generated ID token;
- properly configured SDUTIL;
- created Seismic Store's `tenant` and `subproject` with access to it.


Copy the file from your local machine to Seismic Store:

```shell
python sdutil cp /path/to/local/segy/file sd://<tenant>/<subproject>/<some_path>/<file_name> --idtoken=$ID_TOKEN
```

From this point your Segy-file is available as a dataset in Seismic Store.

To get the dataset's short info:

```shell
python sdutil stat sd://<tenant>/<subproject>/<some_path>/<file_name> --idtoken=$ID_TOKEN
```

Sometimes it is required to unlock your uploaded dataset

```shell
python sdutil unlock sd://<tenant>/<subproject>/<path>/<file_name>  --idtoken=$ID_TOKEN
```

`sd://<tenant>/<subproject>/<some_path>/<file_name>` is URI to address your dataset. With this URI you will work in the next steps.

### Start Segy -> OpenVDS conversion workflow

After you uploaded the file on Seismic Store, you can start the conversion workflow:

```shell
curl --location --request POST '<workflow_host>/v1/workflow/Segy_to_vds_conversion_sdms/workflowRun' \
--header 'data-partition-id: <data-partition-id>' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data-raw '{
    "executionContext": {
        "Payload": {
            "AppKey": "test-app",
            "data-partition-id": "<data-partition-id>"
        },
        "vds_url": "sd://<tenant>/<subproject>/<path>",
        "persistent_id": "<unique name of vds conversion>",
        "id_token": <id_token>
        "segy_url": "sd://<tenant>/<subproject>/<path>/<segy_name>"
    }
```

The following fields:

- `vds_url` - the part of the OpenVDS dataset Seismic Store URI consisting of `tenant`, `subproject`, and `path`;

- `persistent_id` - unique ID of the dataset, can be considered the dataset's name;

- `segy_url` - Segy-file Seismic Store URI.

The full Seismic Store URI of OpenVDS dataset will look like `sd://<tenant>/<subproject>/<path>/<persistent_id>`.

To verify that OpenVDS was created successfully:

```shell
python sdutil stat sd://<tenant>/<subproject>/<path>/<persistent_id> --idtoken=$ID_TOKEN
```

or

```
curl --location --request GET '<seismic_store_host>/api/v3/dataset/tenant/<tenant>/subproject/<subproject>/dataset/<persistent_id>?path=<path>&seismicmeta=true' \
--header 'Authorization: Bearer <id_token>' \
--header 'data-partition-id: <data-partition-id>'
```

