from prefect import flow, get_run_logger

from tasks.extract import scrap_data
from tasks.transform import text_to_json
from tasks.load import data_to_api

@flow
def flujo_etl_inmobiliario(url: str, api_url:str):
    logger = get_run_logger()
    
    logger.info("Starting data extraction")
    raw_data = scrap_data(url = url)
    logger.info("Extracted data successfully")
    
    logger.info("Starting data transformation")
    transformed_data = text_to_json(raw_data)
    logger.info("Transformed data successfully")
    
    logger.info("Starting data loading")
    data_to_api(data = transformed_data, api_url= api_url)
    logger.info("Data loading completed successfully")
    logger.info("Closing the flow")