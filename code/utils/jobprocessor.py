import requests
from config import setting
import uuid


def create_job_run(dag_id, inputs):
    # Make URL for the job processor's DAG run
    # https://job-processor.mapmycrop.store/api/v1/dags/Farms_Indices_Values/dagRuns
    url = "{0}/api/v1/dags/{1}/dagRuns".format(setting.JOB_PROCESSOR_API_URL, dag_id)

    # Make a new guid
    guid = uuid.uuid4()
    payload = {"conf": inputs, "dag_run_id": str(guid)}

    req = requests.post(
        url,
        json=payload,
        auth=(setting.JOB_PROCESSOR_USER, setting.JOB_PROCESSOR_PASSWORD),
    )
    if req.status_code == 200:
        return req.json()
    else:
        print("Error creating job run", req.status_code, req.text)
        return None


def get_job_status(dag_id, run_id):
    # Make URL for the job processor's DAG run
    # https://job-processor.mapmycrop.store/api/v1/dags/Farms_Indices_Values/dagRuns/ba424e72-2300-429b-bfdb-16498f94cbf8
    url = "{0}/api/v1/dags/{1}/dagRuns/{2}".format(
        setting.JOB_PROCESSOR_API_URL, dag_id, run_id
    )

    req = requests.get(
        url, auth=(setting.JOB_PROCESSOR_USER, setting.JOB_PROCESSOR_PASSWORD)
    )
    if req.status_code == 200:
        return req.json()
    else:
        print("Error getting job status", req.status_code, req.text)
        return None


def get_job_xCom(dag_id, run_id, task_id, key):
    # Make URL for the job processor's xcomEnteries
    # https://job-processor.mapmycrop.store/api/v1/dags/Farms_Indices_Values/dagRuns/ba424e72-2300-429b-bfdb-16498f94cbf8/taskInstances/get_farm_indices_values/xcomEntries/return_value
    url = "{0}/api/v1/dags/{1}/dagRuns/{2}/taskInstances/{3}/xcomEntries/{4}".format(
        setting.JOB_PROCESSOR_API_URL, dag_id, run_id, task_id, key
    )

    req = requests.get(
        url, auth=(setting.JOB_PROCESSOR_USER, setting.JOB_PROCESSOR_PASSWORD)
    )
    if req.status_code == 200:
        return req.json()["value"]
    else:
        print("Error getting job Output", req.status_code, req.text)
        return None
