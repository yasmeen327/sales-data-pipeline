import pandas as pd
import psycopg2
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PARAMS = {
    'host': 'localhost',
    'database': 'sales_db',
    'user': 'pipeline_user',
    'password': 'mypassword'
}

def ingest_csv_to_staging(csv_file):
    logger.info(f"Starting ingestion from {csv_file}")
    
    df = pd.read_csv(csv_file)
    logger.info(f"Read {len(df)} records from CSV")
    
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['total_amount'] = df['total_amount'].round(2)
    df = df.fillna({'quantity': 1, 'unit_price': 0})
    
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    # Clear staging table
    cursor.execute("TRUNCATE TABLE staging.sales_raw;")
    logger.info("Truncated staging table")
    
    # Insert records
    inserted = 0
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO staging.sales_raw 
                (order_id, customer_id, product_id, product_name, category, 
                 quantity, unit_price, total_amount, order_date, region)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['order_id'], row['customer_id'], row['product_id'],
                row['product_name'], row['category'], row['quantity'],
                row['unit_price'], row['total_amount'], row['order_date'],
                row['region']
            ))
            inserted += 1
            
            if inserted % 1000 == 0:
                logger.info(f"Ingested {inserted} records")
                conn.commit()
        except Exception as e:
            logger.error(f"Error inserting order {row['order_id']}: {e}")
    
    conn.commit()
    logger.info(f"✓ Successfully inserted {inserted} records")
    
    cursor.close()
    conn.close()
    return inserted

if __name__ == "__main__":
    count = ingest_csv_to_staging('sales_data.csv')
    print(f"Ingestion complete! Added {count} records to staging.sales_raw")
