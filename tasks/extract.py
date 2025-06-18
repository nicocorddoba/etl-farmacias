from prefect import task, get_run_logger
from plugins.scrap import run as scrap_run

@task
def scrap_data(url: str,fb_email: str, fb_password: str):
    try:
        logger = get_run_logger()
        image_bytes = scrap_run(url, logger, fb_email, fb_password)
    except Exception as e:
        logger.error(f"Error during data extraction: {e}")
        raise e
    return image_bytes