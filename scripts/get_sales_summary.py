import pandas as pd
import sqlite3
import logging
from Ingestion_db import ingest_db
import time

logger2 = logging.getLogger(__name__)
handler2 = logging.FileHandler('retail_logs/get_sales_summary.log', mode='w')
formatter2 = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler2.setFormatter(formatter2)
logger2.addHandler(handler2)
logger2.setLevel(logging.DEBUG)

logger2.info("Logging from get_sales_summary")


'''logging.basicConfig(
    filename="retail_logs/Injestion.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w"
)'''

def sales_summary(conn):
    "This function will create a summary table by merging and aggregating different tables and add new columns to resultant table"
    Summary_Table=pd.read_sql_query("""
    with Customers_Summary as(
    select 
    c.customerkey,
    s.productkey,
    s.storekey,
    c.name,
    c.city,
    c.state,
    c.country,
    sum(s.quantity) as Total_Quantity
    from customers c
    left join
    sales s
    on c.customerkey=s.customerkey
    group by c.customerkey,c.name,s.productkey,s.storekey,
    c.city,
    c.state,
    c.country
    ),

    Products_Summary as(

    select productkey,
    product_name,
    category,
    sum(unit_cost_usd) as Unit_Cost_USD,
    sum(unit_price_usd) as Unit_Price_USD
    from products
    group by productkey,
    product_name,
    category
    ),

    Stores_Summary as(
    select storekey,
    state as Store_State,
    country as Store_Country
    from stores
    )

    select 
    cs.Customerkey as Customer_ID,
    cs.name as Customer_Name,
    cs.city,
    cs.state,
    cs.country,
    ps.product_name,
    ps.category,
    ss.storekey,
    ss.Store_State,
    ss.Store_Country,
    cs.Total_Quantity,
    ps.Unit_Cost_USD,
    ps.Unit_Price_USD

    from Customers_Summary as cs
    join Products_Summary as ps
    on cs.productkey=ps.productkey

    join Stores_Summary as ss
    on cs.storekey=ss.storekey

    order by ps.Unit_Price_USD


    """,conn)
    
    return Summary_Table

def clean_data(Summary_Table):
    'This function will clean the data'
    
    #Creating new columns for better analysis
    Summary_Table['Total_Cost']=Summary_Table['Unit_Cost_USD']*Summary_Table['Total_Quantity']
    Summary_Table['Total_Sales']=Summary_Table['Unit_Price_USD']*Summary_Table['Total_Quantity']
    Summary_Table['Gross_Profit']=Summary_Table['Total_Sales']-Summary_Table['Total_Cost']
    Summary_Table['Gross_Margin']=round(Summary_Table['Gross_Profit']/Summary_Table['Total_Sales'],2)
    
    return Summary_Table


if __name__=="__main__":
    
    start=time.time()
    
    conn=sqlite3.connect("retail.db")
    
    logger2.info("Creating Sales summary table")
    summary_df=sales_summary(conn)
    logger2.info(summary_df.head())
    
    logger2.info("Cleaning Sales summary table")
    cleaned_df=clean_data(summary_df)
    logger2.info(cleaned_df.head())
    
    logger2.info("Ingesting Sales summary table to database")
    ingest_db(cleaned_df,'Summary_Table',conn)
    end=time.time()
    Total_Time=(end-start)/60
    logger2.info("Completed")
    logger2.info(f"Total time taken {Total_Time} minutes")
                 
