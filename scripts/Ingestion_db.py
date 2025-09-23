import pandas as pd
from sqlalchemy import create_engine
import os
import logging
import time

logger1 = logging.getLogger('Ingestion_db')
handler1 = logging.FileHandler('retail_logs/Ingestion.log', mode='w')
formatter1 = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler1.setFormatter(formatter1)
logger1.addHandler(handler1)
logger1.setLevel(logging.DEBUG)

logger1.info("Logging from Ingestion_db")

'''logging.basicConfig(
    filename="retail_logs/Injestion.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w"
)'''

engine=create_engine('sqlite:///retail.db')

def ingest_db(df,tablename,enigne):
    #This function will ingest the dataframe into databsae table
    df.to_sql(tablename,con=engine,if_exists='replace',index=False)
    
    
def load_raw_data():
    start=time.time()
    #This function will load CSV files as dataframe and ingest into database
    for file in os.listdir('Global_Electronics_Retailer_data'):
        path='Global_Electronics_Retailer_data/'+file
        logger1.info(f"Ingesting {file} into database")
        try:
            df = pd.read_csv(path, encoding='utf-8')
        except UnicodeDecodeError:
            logger1.info(f"UTF-8 failed for {file}, trying Latin-1...")
            df = pd.read_csv(path, encoding='latin-1') 

        ingest_db(df,file[:-4],engine)
    end=time.time()
    total_time=(end-start)/60
    logger1.info(f"Ingestion Complete\n")
    logger1.info(f"Total time taken : {total_time} minutes")
    
if __name__=="__main__":
    load_raw_data()