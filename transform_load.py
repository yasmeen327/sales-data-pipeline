import psycopg2
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PARAMS = {
    'host': 'localhost',
    'database': 'sales_db',
    'user': 'pipeline_user',
    'password': 'mypassword'
}

def transform_and_load():
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    logger.info("Starting transformation process")
    
    # Update product dimension
    logger.info("Updating product dimension")
    cursor.execute("""
        DELETE FROM warehouse.dim_products;
        INSERT INTO warehouse.dim_products (product_id, product_name, category, current_price, last_updated)
        SELECT DISTINCT 
            product_id,
            product_name,
            category,
            unit_price,
            CURRENT_DATE
        FROM staging.sales_raw
        ORDER BY product_id;
    """)
    logger.info(f"Updated {cursor.rowcount} products")
    
    # Update region dimension
    logger.info("Updating region dimension")
    cursor.execute("""
        DELETE FROM warehouse.dim_regions;
        INSERT INTO warehouse.dim_regions (region_name, country)
        SELECT DISTINCT region, 'USA' FROM staging.sales_raw;
    """)
    logger.info(f"Updated {cursor.rowcount} regions")
    
    # Load fact table
    logger.info("Loading fact table")
    cursor.execute("""
        DELETE FROM warehouse.fact_sales;
        INSERT INTO warehouse.fact_sales 
        (order_id, customer_id, product_id, region_id, quantity, total_amount, order_date)
        SELECT 
            s.order_id,
            s.customer_id,
            s.product_id,
            r.region_id,
            s.quantity,
            s.total_amount,
            s.order_date
        FROM staging.sales_raw s
        JOIN warehouse.dim_regions r ON s.region = r.region_name;
    """)
    logger.info(f"Loaded {cursor.rowcount} fact records")
    
    conn.commit()
    logger.info("✓ Transformation and load completed")
    
    cursor.close()
    conn.close()

def verify_data():
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM warehouse.fact_sales")
    fact_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM warehouse.dim_products")
    product_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM warehouse.dim_regions")
    region_count = cursor.fetchone()[0]
    
    logger.info(f"Verification: {fact_count} fact records, {product_count} products, {region_count} regions")
    
    # Show sample
    cursor.execute("""
        SELECT f.order_id, p.product_name, r.region_name, f.total_amount, f.order_date
        FROM warehouse.fact_sales f
        JOIN warehouse.dim_products p ON f.product_id = p.product_id
        JOIN warehouse.dim_regions r ON f.region_id = r.region_id
        LIMIT 5;
    """)
    
    print("\n📋 Sample data in warehouse:")
    for row in cursor.fetchall():
        print(f"   Order {row[0]}: {row[1]} sold in {row[2]} for ${row[3]:.2f} on {row[4]}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    transform_and_load()
    verify_data()
