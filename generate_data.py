import pandas as pd
import random
from datetime import datetime, timedelta

def generate_sales_data(n_records=10000):
    products = [
        (1, 'Laptop', 'Electronics', 999.99),
        (2, 'Mouse', 'Electronics', 25.99),
        (3, 'Desk Chair', 'Furniture', 199.99),
        (4, 'Coffee Mug', 'Kitchen', 12.99),
        (5, 'Notebook', 'Office', 4.99),
        (6, 'Monitor', 'Electronics', 299.99),
        (7, 'Keyboard', 'Electronics', 79.99),
        (8, 'Desk Lamp', 'Furniture', 45.99),
        (9, 'Water Bottle', 'Sports', 19.99),
        (10, 'Backpack', 'Accessories', 59.99)
    ]
    
    regions = ['North', 'South', 'East', 'West']
    customers = range(1, 501)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    data = []
    for i in range(1, n_records + 1):
        product_id, product_name, category, price = random.choice(products)
        quantity = random.randint(1, 5)
        total = round(price * quantity, 2)
        order_date = start_date + timedelta(days=random.randint(0, 365))
        
        data.append({
            'order_id': i,
            'customer_id': random.choice(customers),
            'product_id': product_id,
            'product_name': product_name,
            'category': category,
            'quantity': quantity,
            'unit_price': price,
            'total_amount': total,
            'order_date': order_date,
            'region': random.choice(regions)
        })
    
    df = pd.DataFrame(data)
    df.to_csv('sales_data.csv', index=False)
    print(f"✓ Generated {n_records} records and saved to sales_data.csv")
    print("\nSample of generated data:")
    print(df.head())
    return df

if __name__ == "__main__":
    generate_sales_data(10000)
