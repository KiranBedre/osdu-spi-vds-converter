# Segy to Vds Conversion

Airflow DAG for transformation from SEGY to OpenVDS

###Registering a Workflow
```
curl --location --request POST 'https://<base_url>/api/workflow/v1/workflow' \
--header 'Content-Type: application/json' \
--header 'data-partition-id: opendes' \
--header 'Authorization: <Bearer Token>' \
--data-raw '{
    "description": "SegY To OpenVDS Conversion",
    "registrationInstructions": {
        "dagName": "openvds_import "
    },
    "workflowName": "openvds_import"
}'
```
Note: THe WorkflowName should be the Dag name registered with Airflow

Expected Output
```
{
    "workflowId": "opendes:openvds_import",
    "workflowName": "openvds_import",
    "description": "SegY To OpenVDS Conversion",
    "createdBy": "admin@testing.com",
    "creationTimestamp": 1617297515622,
    "version": 1617297515622
}
```



###Triggering Workflow

Configuring the input, url connection and target location, see the 

```
curl --location --request POST 'https://<base_url>/api/workflow/v1/workflow/openvds_import/workflowRun' \
--header 'Content-Type: application/json' \
--header 'data-partition-id: opendes' \
--header 'Authorization: <Bearer Token>' \
--data-raw '{
    "executionContext": {
        "url_connection":"Region=us-east-1;AccessKeyId=XXX;SecretKey=XXX;SessionToken=XXX",
        "input_connection":"Region=us-east-1;AccessKeyId=XXX;SecretKey=XXX;SessionToken=XXX",
        "segy_file":"s3://aws-osdu-sample-data/sample-data/seismic/st0202/stacks/ST0202R08_PS_PSDM_RAW_PP_TIME.MIG_RAW.POST_STACK.3D.JS-017534.segy",
        "url":"s3://aws-osdu-sample-data/"
    }
}
'
```
Expected output
```
{
    "workflowId": "opendes:openvds_import",
    "runId": "3e73eb98-69d3-48c9-bf1e-ab967d2dba91",
    "startTimeStamp": 1617297632023,
    "status": "submitted",
    "submittedBy": "admin@testing.com"
}
```



Example of Dag Run Success
```
*** Reading remote log from s3://osdu-wanzhiji-ingest-s3airflowbucketdev-11h61ldwb6zv2/logs/openvds_import/OPENVDS/2021-04-01T16:47:25.432823+00:00/1.log.
[2021-04-01 16:47:33,245] {taskinstance.py:670} INFO - Dependencies all met for <TaskInstance: openvds_import.OPENVDS 2021-04-01T16:47:25.432823+00:00 [queued]>
[2021-04-01 16:47:33,268] {taskinstance.py:670} INFO - Dependencies all met for <TaskInstance: openvds_import.OPENVDS 2021-04-01T16:47:25.432823+00:00 [queued]>
[2021-04-01 16:47:33,268] {taskinstance.py:880} INFO - 
--------------------------------------------------------------------------------
[2021-04-01 16:47:33,268] {taskinstance.py:881} INFO - Starting attempt 1 of 1
[2021-04-01 16:47:33,268] {taskinstance.py:882} INFO - 
--------------------------------------------------------------------------------
[2021-04-01 16:47:33,284] {taskinstance.py:901} INFO - Executing <Task(KubernetesPodOperator): OPENVDS> on 2021-04-01T16:47:25.432823+00:00
[2021-04-01 16:47:33,287] {standard_task_runner.py:54} INFO - Started process 216 to run task
[2021-04-01 16:47:33,319] {standard_task_runner.py:77} INFO - Running: ['airflow', 'run', 'openvds_import', 'OPENVDS', '2021-04-01T16:47:25.432823+00:00', '--job_id', '117', '--pool', 'default_pool', '--raw', '-sd', 'DAGS_FOLDER/openvds/openvds.py', '--cfg_path', '/tmp/tmprpvc0je2']
[2021-04-01 16:47:33,320] {standard_task_runner.py:78} INFO - Job 117: Subtask OPENVDS
[2021-04-01 16:47:33,383] {logging_mixin.py:112} INFO - Running <TaskInstance: openvds_import.OPENVDS 2021-04-01T16:47:25.432823+00:00 [running]> on host 67371a44eba7
[2021-04-01 16:47:34,205] {logging_mixin.py:112} WARNING - /usr/local/lib/python3.8/site-packages/airflow/kubernetes/pod_launcher.py:309: DeprecationWarning: Using `airflow.contrib.kubernetes.pod.Pod` is deprecated. Please use `k8s.V1Pod`.
  dummy_pod = Pod(
[2021-04-01 16:47:34,205] {logging_mixin.py:112} WARNING - /usr/local/lib/python3.8/site-packages/airflow/kubernetes/pod_launcher.py:77: DeprecationWarning: Using `airflow.contrib.kubernetes.pod.Pod` is deprecated. Please use `k8s.V1Pod` instead.
  pod = self._mutate_pod_backcompat(pod)
[2021-04-01 16:47:34,272] {pod_launcher.py:171} INFO - Event: openvds-9d1ddefd4b5f4268b50af564cde10795 had an event of type Pending
[2021-04-01 16:47:34,272] {pod_launcher.py:139} WARNING - Pod not yet started: openvds-9d1ddefd4b5f4268b50af564cde10795
[2021-04-01 16:47:35,283] {pod_launcher.py:171} INFO - Event: openvds-9d1ddefd4b5f4268b50af564cde10795 had an event of type Pending
[2021-04-01 16:47:35,284] {pod_launcher.py:139} WARNING - Pod not yet started: openvds-9d1ddefd4b5f4268b50af564cde10795
[2021-04-01 16:47:36,298] {pod_launcher.py:171} INFO - Event: openvds-9d1ddefd4b5f4268b50af564cde10795 had an event of type Running
[2021-04-01 16:47:48,547] {pod_launcher.py:156} INFO - b'\n'
[2021-04-01 16:47:48,547] {pod_launcher.py:156} INFO - b'Importing into: s3://aws-osdu-sample-data/515D714B13377CAD\n'
[2021-04-01 16:47:48,547] {pod_launcher.py:156} INFO - b'\n'
[2021-04-01 16:47:48,547] {pod_launcher.py:156} INFO - b'\r100% done processing s3://aws-osdu-sample-data/515D714B13377CAD.\n'
[2021-04-01 16:47:49,573] {pod_launcher.py:171} INFO - Event: openvds-9d1ddefd4b5f4268b50af564cde10795 had an event of type Succeeded
[2021-04-01 16:47:49,573] {pod_launcher.py:287} INFO - Event with job id openvds-9d1ddefd4b5f4268b50af564cde10795 Succeeded
[2021-04-01 16:47:49,584] {pod_launcher.py:171} INFO - Event: openvds-9d1ddefd4b5f4268b50af564cde10795 had an event of type Succeeded
[2021-04-01 16:47:49,584] {pod_launcher.py:287} INFO - Event with job id openvds-9d1ddefd4b5f4268b50af564cde10795 Succeeded
[2021-04-01 16:47:49,625] {taskinstance.py:1057} INFO - Marking task as SUCCESS.dag_id=openvds_import, task_id=OPENVDS, execution_date=20210401T164725, start_date=20210401T164733, end_date=20210401T164749
[2021-04-01 16:47:53,332] {local_task_job.py:102} INFO - Task exited with return code 0
```



Example of Dag Run Failed
```
*** Reading remote log from s3://osdu-wanzhiji-ingest-s3airflowbucketdev-11h61ldwb6zv2/logs/openvds_import/OPENVDS/2021-04-01T16:33:10.782063+00:00/1.log.
[2021-04-01 16:33:16,145] {taskinstance.py:670} INFO - Dependencies all met for <TaskInstance: openvds_import.OPENVDS 2021-04-01T16:33:10.782063+00:00 [queued]>
[2021-04-01 16:33:16,169] {taskinstance.py:670} INFO - Dependencies all met for <TaskInstance: openvds_import.OPENVDS 2021-04-01T16:33:10.782063+00:00 [queued]>
[2021-04-01 16:33:16,169] {taskinstance.py:880} INFO - 
--------------------------------------------------------------------------------
[2021-04-01 16:33:16,169] {taskinstance.py:881} INFO - Starting attempt 1 of 1
[2021-04-01 16:33:16,169] {taskinstance.py:882} INFO - 
--------------------------------------------------------------------------------
[2021-04-01 16:33:16,184] {taskinstance.py:901} INFO - Executing <Task(KubernetesPodOperator): OPENVDS> on 2021-04-01T16:33:10.782063+00:00
[2021-04-01 16:33:16,187] {standard_task_runner.py:54} INFO - Started process 178 to run task
[2021-04-01 16:33:16,219] {standard_task_runner.py:77} INFO - Running: ['airflow', 'run', 'openvds_import', 'OPENVDS', '2021-04-01T16:33:10.782063+00:00', '--job_id', '112', '--pool', 'default_pool', '--raw', '-sd', 'DAGS_FOLDER/openvds/openvds.py', '--cfg_path', '/tmp/tmpl63qcsu6']
[2021-04-01 16:33:16,219] {standard_task_runner.py:78} INFO - Job 112: Subtask OPENVDS
[2021-04-01 16:33:16,280] {logging_mixin.py:112} INFO - Running <TaskInstance: openvds_import.OPENVDS 2021-04-01T16:33:10.782063+00:00 [running]> on host 67371a44eba7
[2021-04-01 16:33:17,260] {logging_mixin.py:112} WARNING - /usr/local/lib/python3.8/site-packages/airflow/kubernetes/pod_launcher.py:309: DeprecationWarning: Using `airflow.contrib.kubernetes.pod.Pod` is deprecated. Please use `k8s.V1Pod`.
  dummy_pod = Pod(
[2021-04-01 16:33:17,261] {logging_mixin.py:112} WARNING - /usr/local/lib/python3.8/site-packages/airflow/kubernetes/pod_launcher.py:77: DeprecationWarning: Using `airflow.contrib.kubernetes.pod.Pod` is deprecated. Please use `k8s.V1Pod` instead.
  pod = self._mutate_pod_backcompat(pod)
[2021-04-01 16:33:17,522] {pod_launcher.py:171} INFO - Event: openvds-b46f116bd78346fdb88c86444edd448d had an event of type Pending
[2021-04-01 16:33:17,522] {pod_launcher.py:139} WARNING - Pod not yet started: openvds-b46f116bd78346fdb88c86444edd448d
[2021-04-01 16:33:18,534] {pod_launcher.py:171} INFO - Event: openvds-b46f116bd78346fdb88c86444edd448d had an event of type Pending
[2021-04-01 16:33:18,535] {pod_launcher.py:139} WARNING - Pod not yet started: openvds-b46f116bd78346fdb88c86444edd448d
[2021-04-01 16:33:19,545] {pod_launcher.py:171} INFO - Event: openvds-b46f116bd78346fdb88c86444edd448d had an event of type Pending
[2021-04-01 16:33:19,546] {pod_launcher.py:139} WARNING - Pod not yet started: openvds-b46f116bd78346fdb88c86444edd448d
[2021-04-01 16:33:20,555] {pod_launcher.py:171} INFO - Event: openvds-b46f116bd78346fdb88c86444edd448d had an event of type Pending
[2021-04-01 16:33:20,555] {pod_launcher.py:139} WARNING - Pod not yet started: openvds-b46f116bd78346fdb88c86444edd448d
[2021-04-01 16:33:21,565] {pod_launcher.py:171} INFO - Event: openvds-b46f116bd78346fdb88c86444edd448d had an event of type Pending
[2021-04-01 16:33:21,565] {pod_launcher.py:139} WARNING - Pod not yet started: openvds-b46f116bd78346fdb88c86444edd448d
[2021-04-01 16:33:22,575] {pod_launcher.py:171} INFO - Event: openvds-b46f116bd78346fdb88c86444edd448d had an event of type Pending
[2021-04-01 16:33:22,575] {pod_launcher.py:139} WARNING - Pod not yet started: openvds-b46f116bd78346fdb88c86444edd448d
[2021-04-01 16:33:23,586] {pod_launcher.py:171} INFO - Event: openvds-b46f116bd78346fdb88c86444edd448d had an event of type Pending
[2021-04-01 16:33:23,586] {pod_launcher.py:139} WARNING - Pod not yet started: openvds-b46f116bd78346fdb88c86444edd448d
[2021-04-01 16:33:24,597] {pod_launcher.py:171} INFO - Event: openvds-b46f116bd78346fdb88c86444edd448d had an event of type Failed
[2021-04-01 16:33:24,597] {pod_launcher.py:284} INFO - Event with job id openvds-b46f116bd78346fdb88c86444edd448d Failed
[2021-04-01 16:33:24,631] {pod_launcher.py:156} INFO - b'Could not open:  - File::open \x00No such file or directory\n'
[2021-04-01 16:33:24,655] {pod_launcher.py:171} INFO - Event: openvds-b46f116bd78346fdb88c86444edd448d had an event of type Failed
[2021-04-01 16:33:24,655] {pod_launcher.py:284} INFO - Event with job id openvds-b46f116bd78346fdb88c86444edd448d Failed
[2021-04-01 16:33:24,664] {pod_launcher.py:171} INFO - Event: openvds-b46f116bd78346fdb88c86444edd448d had an event of type Failed
[2021-04-01 16:33:24,665] {pod_launcher.py:284} INFO - Event with job id openvds-b46f116bd78346fdb88c86444edd448d Failed
[2021-04-01 16:33:24,704] {taskinstance.py:1150} ERROR - Pod Launching failed: Pod returned a failure: failed
Traceback (most recent call last):
  File "/usr/local/lib/python3.8/site-packages/airflow/contrib/operators/kubernetes_pod_operator.py", line 308, in execute
    raise AirflowException(
airflow.exceptions.AirflowException: Pod returned a failure: failed

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.8/site-packages/airflow/models/taskinstance.py", line 984, in _run_raw_task
    result = task_copy.execute(context=context)
  File "/usr/local/lib/python3.8/site-packages/airflow/contrib/operators/kubernetes_pod_operator.py", line 312, in execute
    raise AirflowException('Pod Launching failed: {error}'.format(error=ex))
airflow.exceptions.AirflowException: Pod Launching failed: Pod returned a failure: failed
[2021-04-01 16:33:24,709] {taskinstance.py:1187} INFO - Marking task as FAILED. dag_id=openvds_import, task_id=OPENVDS, execution_date=20210401T163310, start_date=20210401T163316, end_date=20210401T163324
[2021-04-01 16:33:26,147] {local_task_job.py:102} INFO - Task exited with return code 1
```