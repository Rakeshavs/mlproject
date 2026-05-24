import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mlproject.logger import logging
from mlproject.exception import CustomException
from mlproject.components.data_ingestion import DataIngestion
from mlproject.components.data_ingestion import DataIngestionConfig
if __name__=="__main__":
    logging.info("Starting the application")
   
    try:
        data_ingestion = DataIngestion()
        #data_ingestion_config = DataIngestionConfig()
        train_data, test_data = data_ingestion.initiate_data_ingestion()
        data_ingestion.initiate_data_ingestion()
    except Exception as e:
        logging.info("Exception custom exception")
        raise CustomException(e, sys)