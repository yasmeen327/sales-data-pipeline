-- staging schema tables
CREATE TABLE IF NOT EXISTS staging.sales_raw (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    product_id INTEGER,
    product_name VARCHAR(200),
    category VARCHAR(100),
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    order_date DATE,
    region VARCHAR(50),
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- warehouse dimension tables
CREATE TABLE IF NOT EXISTS warehouse.dim_products (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(200),
    category VARCHAR(100),
    current_price DECIMAL(10,2),
    last_updated DATE
);

CREATE TABLE IF NOT EXISTS warehouse.dim_regions (
    region_id SERIAL PRIMARY KEY,
    region_name VARCHAR(50) UNIQUE,
    country VARCHAR(50)
);

-- warehouse fact table
CREATE TABLE IF NOT EXISTS warehouse.fact_sales (
    sale_id SERIAL PRIMARY KEY,
    order_id INTEGER UNIQUE,
    customer_id INTEGER,
    product_id INTEGER,
    region_id INTEGER,
    quantity INTEGER,
    total_amount DECIMAL(10,2),
    order_date DATE,
    etl_processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES warehouse.dim_products(product_id),
    FOREIGN KEY (region_id) REFERENCES warehouse.dim_regions(region_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_fact_sales_order_date ON warehouse.fact_sales(order_date);
CREATE INDEX IF NOT EXISTS idx_fact_sales_product ON warehouse.fact_sales(product_id);
