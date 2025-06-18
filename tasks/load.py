from prefect import task, get_run_logger
import requests
import json

@task
def data_to_api(data:json, api_url:str):
    try:
        logger = get_run_logger()
        r = requests.post(url=api_url, data=data)
        logger.info(r.content)
        logger.info(r.status_code)
    except requests.HTTPError as e:
        logger.info("ERROR HTTP en la carga de datos")
        raise e