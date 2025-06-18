from prefect import flow, get_run_logger

from tasks.extract import scrap_data
from tasks.transform import text_to_json
from tasks.load import data_to_api

@flow
def flujo_carga_api(api_url:str, fb_url: str, fb_email: str, fb_password: str):
    logger = get_run_logger()
    
    logger.info("Starting data extraction")
    image_bytes = scrap_data(url = fb_url, fb_email=fb_email, fb_password=fb_password)
    logger.info("Extracted data successfully")
    
    logger.info("Starting data transformation")
    transformed_data = text_to_json(image_bytes)
    logger.info("Transformed data successfully")
    
    logger.info("Starting data loading")
    data_to_api(data = transformed_data, api_url= api_url)
    logger.info("Data loading completed successfully")
    logger.info("Closing the flow")