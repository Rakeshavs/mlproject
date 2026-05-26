import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mlproject.logger import logging
from mlproject.exception import CustomException
from mlproject.components.data_ingestion import DataIngestion
from mlproject.components.data_ingestion import DataIngestionConfig
from mlproject.components.data_transformation import DataTransformationConfig,DataTransformation
from mlproject.components.model_trainer import ModelTrainerConfig,ModelTrainer

try:
    import dagshub
except ImportError:
    dagshub = None
if __name__=="__main__":
    logging.info("Starting the application")
   
    try:
        data_ingestion = DataIngestion()
        train_data, test_data = data_ingestion.initiate_data_ingestion()

        data_transformation = DataTransformation()
        train_arr, test_arr, _ = data_transformation.initiate_data_transformation(
            train_path=train_data,
            test_path=test_data
        )

        if dagshub is not None:
            dagshub_repo_owner = os.getenv("DAGSHUB_REPO_OWNER", "Rakeshavs")
            dagshub_repo_name = os.getenv("DAGSHUB_REPO_NAME", "mlproject")
            dagshub_init_mlflow = os.getenv("DAGSHUB_INIT_MLFLOW", "true").lower() in ("1", "true", "yes")
            if dagshub_init_mlflow:
                dagshub.init(
                    repo_owner=dagshub_repo_owner,
                    repo_name=dagshub_repo_name,
                    mlflow=True,
                )
                logging.info(
                    f"Initialized Dagshub for {dagshub_repo_owner}/{dagshub_repo_name}"
                )
        else:
            logging.warning("dagshub package not installed; skipping Dagshub initialization.")

        # MODEL TRAINING
        model_trainer = ModelTrainer()
        print(model_trainer.initiate_model_trainer(train_array=train_arr, test_array=test_arr))
        
    except Exception as e:
        logging.info("Exception custom exception")
        raise CustomException(e, sys)