import psycopg2
from datetime import datetime

# Using peer authentication (no password needed when running as your user)
DB_PARAMS = {
    'host': 'localhost',
    'database': 'sales_db',
    'user': 'kiwilytics',  # Your Ubuntu username
    'password': ''
}

def check_pipeline():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        print("\n🔍 PIPELINE STATUS CHECK")
        print("="*40)
        
        # Check staging
        cursor.execute("SELECT COUNT(*) FROM staging.sales_raw")
        staging_count = cursor.fetchone()[0]
        print(f"✅ Staging: {staging_count:,} records")
        
        # Check dimensions
        cursor.execute("SELECT COUNT(*) FROM warehouse.dim_products")
        products = cursor.fetchone()[0]
        print(f"✅ Products: {products} dimensions")
        
        cursor.execute("SELECT COUNT(*) FROM warehouse.dim_regions")
        regions = cursor.fetchone()[0]
        print(f"✅ Regions: {regions} dimensions")
        
        # Check fact table
        cursor.execute("SELECT COUNT(*) FROM warehouse.fact_sales")
        fact_count = cursor.fetchone()[0]
        print(f"✅ Fact Table: {fact_count:,} records")
        
        # Check data freshness
        cursor.execute("SELECT MAX(etl_processed_at) FROM warehouse.fact_sales")
        last_run = cursor.fetchone()[0]
        print(f"⏰ Last ETL Run: {last_run}")
        
        cursor.close()
        conn.close()
        
        if staging_count == fact_count and staging_count > 0:
            print("\n🎉 PIPELINE HEALTHY - All records processed!")
        else:
            print(f"\n⚠️ Warning: Staging ({staging_count}) vs Fact ({fact_count}) counts don't match")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("\nTrying alternative connection method...")
        
        # Try with postgres user
        try:
            conn = psycopg2.connect(
                host='localhost',
                database='sales_db',
                user='postgres',
                password=''
            )
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM warehouse.fact_sales")
            count = cursor.fetchone()[0]
            print(f"✅ Connected via postgres user! Fact table has {count:,} records")
            cursor.close()
            conn.close()
        except:
            print("❌ Could not connect. Run: sudo -u postgres psql -d sales_db")

if __name__ == "__main__":
    check_pipeline()
