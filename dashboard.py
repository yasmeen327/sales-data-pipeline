import psycopg2
from datetime import datetime

DB_PARAMS = {
    'host': 'localhost',
    'database': 'sales_db',
    'user': 'pipeline_user',
    'password': 'mypassword'
}

def show_dashboard():
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print(f"📊 SALES DASHBOARD - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    # Overall metrics
    cursor.execute("""
        SELECT 
            COUNT(*) as total_orders,
            SUM(total_amount) as total_revenue,
            ROUND(AVG(total_amount), 2) as avg_order_value,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM warehouse.fact_sales
    """)
    total_orders, total_revenue, avg_order, unique_customers = cursor.fetchone()
    
    print(f"\n💰 OVERALL METRICS")
    print(f"   Total Orders: {total_orders:,}")
    print(f"   Total Revenue: ${total_revenue:,.2f}")
    print(f"   Average Order Value: ${avg_order:.2f}")
    print(f"   Unique Customers: {unique_customers:,}")
    
    # Top products
    cursor.execute("""
        SELECT p.product_name, SUM(f.total_amount) as revenue, COUNT(*) as orders
        FROM warehouse.fact_sales f
        JOIN warehouse.dim_products p ON f.product_id = p.product_id
        GROUP BY p.product_name
        ORDER BY revenue DESC
        LIMIT 5
    """)
    print(f"\n🏆 TOP 5 PRODUCTS BY REVENUE")
    for i, (product, revenue, orders) in enumerate(cursor.fetchall(), 1):
        print(f"   {i}. {product}: ${revenue:,.2f} ({orders} orders)")
    
    # Regional breakdown
    cursor.execute("""
        SELECT r.region_name, SUM(f.total_amount) as revenue, COUNT(*) as orders
        FROM warehouse.fact_sales f
        JOIN warehouse.dim_regions r ON f.region_id = r.region_id
        GROUP BY r.region_name
        ORDER BY revenue DESC
    """)
    print(f"\n📍 SALES BY REGION")
    for region, revenue, orders in cursor.fetchall():
        print(f"   {region}: ${revenue:,.2f} ({orders} orders)")
    
    # Category analysis
    cursor.execute("""
        SELECT p.category, SUM(f.total_amount) as revenue, COUNT(*) as orders
        FROM warehouse.fact_sales f
        JOIN warehouse.dim_products p ON f.product_id = p.product_id
        GROUP BY p.category
        ORDER BY revenue DESC
    """)
    print(f"\n📦 SALES BY CATEGORY")
    for category, revenue, orders in cursor.fetchall():
        print(f"   {category}: ${revenue:,.2f} ({orders} orders)")
    
    # Best day of week
    cursor.execute("""
        SELECT 
            TO_CHAR(order_date, 'Day') as day_of_week,
            COUNT(*) as orders,
            SUM(total_amount) as revenue
        FROM warehouse.fact_sales
        GROUP BY TO_CHAR(order_date, 'Day'), EXTRACT(DOW FROM order_date)
        ORDER BY EXTRACT(DOW FROM order_date)
    """)
    print(f"\n📅 SALES BY DAY OF WEEK")
    for day, orders, revenue in cursor.fetchall():
        print(f"   {day.strip()}: {orders} orders (${revenue:,.2f})")
    
    cursor.close()
    conn.close()
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    show_dashboard()
