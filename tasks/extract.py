from prefect import task, get_run_logger
from plugins.get_data import get_data

@task
def scrap_data(url: str):
    try:
        url = url
        logger = get_run_logger()
        image_bytes = get_data()
    except Exception as e:
        logger.error(f"Error during data extraction: {e}")
        raise e
    return image_bytes