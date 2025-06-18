from prefect import task, get_run_logger
from plugins.scrap import run as scrap_run

@task
def scrap_data(url: str):
    try:
        logger = get_run_logger()
        img_response = scrap_run(url, logger)
    except Exception as e:
        logger.error(f"Error during data extraction: {e}")
        raise e
    return img_response