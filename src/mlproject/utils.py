import os
import sys
from mlproject.exception import CustomException
from mlproject.logger import logging
import pandas as pd
from dotenv import load_dotenv  
import pymysql
load_dotenv()
host = os.getenv('host')
user = os.getenv('user')
password = os.getenv('password')
db = os.getenv('db')








def read_sql_data():
    logging.info("Entered the read_sql_data method or component")
    try:
        mydb = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=db
        )
        logging.info("Connection to the database is successful")
        df=pd.read_sql('SELECT * FROM students', con=mydb)
        print(df.head())
        return df

    except Exception as ex:
        raise CustomException(ex, sys)