-- Create schemas
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS warehouse;

-- Staging table
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

-- Product dimension (simplified)
CREATE TABLE IF NOT EXISTS warehouse.dim_products (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(200),
    category VARCHAR(100),
    current_price DECIMAL(10,2),
    last_updated DATE
);

-- Region dimension (simplified)
CREATE TABLE IF NOT EXISTS warehouse.dim_regions (
    region_id SERIAL PRIMARY KEY,
    region_name VARCHAR(50)
);

-- Fact table (simplified - no foreign keys initially)
CREATE TABLE IF NOT EXISTS warehouse.fact_sales (
    sale_id SERIAL PRIMARY KEY,
    order_id INTEGER,
    customer_id INTEGER,
    product_id INTEGER,
    region_id INTEGER,
    quantity INTEGER,
    total_amount DECIMAL(10,2),
    order_date DATE,
    etl_processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Simple indexes
CREATE INDEX ON warehouse.fact_sales(order_date);
CREATE INDEX ON warehouse.fact_sales(product_id);
