import os
import sys
from dataclasses import dataclass
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

try:
    import dagshub
    DAGSHUB_AVAILABLE = True
except ImportError:
    dagshub = None
    DAGSHUB_AVAILABLE = False

try:
    import mlflow
    import mlflow.sklearn
    MLFLOW_AVAILABLE = True
except ImportError:
    mlflow = None
    MLFLOW_AVAILABLE = False

DAGSHUB_REPO_OWNER = os.getenv("DAGSHUB_REPO_OWNER", "Rakeshavs")
DAGSHUB_REPO_NAME = os.getenv("DAGSHUB_REPO_NAME", "mlproject")
MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    f"https://dagshub.com/{DAGSHUB_REPO_OWNER}/{DAGSHUB_REPO_NAME}.mlflow",
)
DAGSHUB_INIT_MLFLOW = os.getenv("DAGSHUB_INIT_MLFLOW", "true").lower() in ("1", "true", "yes")
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
try:
    from catboost import CatBoostRegressor
    CATBOOST_AVAILABLE = True
except ImportError:
    CatBoostRegressor = None
    CATBOOST_AVAILABLE = False
from sklearn.ensemble import (
    AdaBoostRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBRegressor = None
    XGBOOST_AVAILABLE = False

from mlproject.exception import CustomException
from mlproject.logger import logging
from mlproject.utils import save_object,evaluate_models


@dataclass
class ModelTrainerConfig:
    trained_model_file_path=os.path.join("artifacts","model.pkl")

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config=ModelTrainerConfig()

    def eval_metrics(self,actual, pred):
        rmse = np.sqrt(mean_squared_error(actual, pred))
        mae = mean_absolute_error(actual, pred)
        r2 = r2_score(actual, pred)
        return rmse, mae, r2

    def initiate_model_trainer(self,train_array,test_array):
        try:
            logging.info("Split training and test input data")
            X_train,y_train,X_test,y_test=(
                train_array[:,:-1],
                train_array[:,-1],
                test_array[:,:-1],
                test_array[:,-1]
            )
            models = {
                "Random Forest": RandomForestRegressor(),
                "Decision Tree": DecisionTreeRegressor(),
                "Gradient Boosting": GradientBoostingRegressor(),
                "Linear Regression": LinearRegression(),
                "AdaBoost Regressor": AdaBoostRegressor(),
            }
            if XGBOOST_AVAILABLE:
                models["XGBRegressor"] = XGBRegressor()
            if CATBOOST_AVAILABLE:
                models["CatBoosting Regressor"] = CatBoostRegressor(verbose=False)
            params={
                "Decision Tree": {
                    'criterion':['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
                    # 'splitter':['best','random'],
                    # 'max_features':['sqrt','log2'],
                },
                "Random Forest":{
                    # 'criterion':['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
                 
                    # 'max_features':['sqrt','log2',None],
                    'n_estimators': [8,16,32,64,128,256]
                },
                "Gradient Boosting":{
                    # 'loss':['squared_error', 'huber', 'absolute_error', 'quantile'],
                    'learning_rate':[.1,.01,.05,.001],
                    'subsample':[0.6,0.7,0.75,0.8,0.85,0.9],
                    # 'criterion':['squared_error', 'friedman_mse'],
                    # 'max_features':['auto','sqrt','log2'],
                    'n_estimators': [8,16,32,64,128,256]
                },
                "Linear Regression":{},
                "XGBRegressor":{
                    'learning_rate':[.1,.01,.05,.001],
                    'n_estimators': [8,16,32,64,128,256]
                },
            }
            if XGBOOST_AVAILABLE:
                params["XGBRegressor"] = {
                    'learning_rate':[.1,.01,.05,.001],
                    'n_estimators': [8,16,32,64,128,256]
                }
            if CATBOOST_AVAILABLE:
                params["CatBoosting Regressor"] = {
                    'depth': [6,8,10],
                    'learning_rate': [0.01, 0.05, 0.1],
                    'iterations': [30, 50, 100]
                }
            params["AdaBoost Regressor"] = {
                'learning_rate':[.1,.01,0.5,.001],
                # 'loss':['linear','square','exponential'],
                'n_estimators': [8,16,32,64,128,256]
            }
            model_report:dict=evaluate_models(X_train,y_train,X_test,y_test,models,params)

            ## To get best model score from dict
            best_model_score = max(sorted(model_report.values()))

             ## To get best model name from dict

            best_model_name = list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]
            best_model = models[best_model_name]

            print("This is the best model:")
            print(best_model_name)

            model_names = list(params.keys())

            actual_model=""

            for model in model_names:
                if best_model_name == model:
                    actual_model = actual_model + model

            best_params = params[actual_model]

            if MLFLOW_AVAILABLE:
                if DAGSHUB_AVAILABLE and DAGSHUB_INIT_MLFLOW:
                    dagshub.init(
                        repo_owner=DAGSHUB_REPO_OWNER,
                        repo_name=DAGSHUB_REPO_NAME,
                        mlflow=True,
                    )

                mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
                tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

                with mlflow.start_run():
                    predicted_qualities = best_model.predict(X_test)
                    (rmse, mae, r2) = self.eval_metrics(y_test, predicted_qualities)
                    mlflow.log_params(best_params)
                    mlflow.log_metric("rmse", rmse)
                    mlflow.log_metric("r2", r2)
                    mlflow.log_metric("mae", mae)

                    if tracking_url_type_store != "file":
                        mlflow.sklearn.log_model(best_model, "model", registered_model_name=actual_model)
                    else:
                        mlflow.sklearn.log_model(best_model, "model")
            else:
                logging.warning("mlflow is not available, skipping mlflow tracking.")

            predicted_qualities = best_model.predict(X_test)
            (rmse, mae, r2) = self.eval_metrics(y_test, predicted_qualities)




            if best_model_score<0.6:
                raise CustomException("No best model found")
            logging.info(f"Best found model on both training and testing dataset")

            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=best_model
            )

            predicted=best_model.predict(X_test)

            r2_square = r2_score(y_test, predicted)
            return r2_square



        except Exception as e:
            raise CustomException(e,sys)