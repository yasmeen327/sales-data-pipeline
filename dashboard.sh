#!/bin/bash

echo "=========================================="
echo "📊 SALES DASHBOARD - $(date '+%Y-%m-%d %H:%M')"
echo "=========================================="

echo ""
echo "💰 OVERALL METRICS"
sudo -u postgres psql -d sales_db -t -c "
SELECT 
    '   Total Orders: ' || COUNT(*) || 
    ' | Total Revenue: $' || TO_CHAR(SUM(total_amount), '999,999,999') ||
    ' | Avg Order: $' || ROUND(AVG(total_amount), 2)
FROM warehouse.fact_sales;"

echo ""
echo "🏆 TOP 3 PRODUCTS"
sudo -u postgres psql -d sales_db -t -c "
SELECT '   ' || ROW_NUMBER() OVER (ORDER BY SUM(f.total_amount) DESC) || '. ' || 
       p.product_name || ': $' || TO_CHAR(SUM(f.total_amount), '999,999')
FROM warehouse.fact_sales f
JOIN warehouse.dim_products p ON f.product_id = p.product_id
GROUP BY p.product_name
ORDER BY SUM(f.total_amount) DESC
LIMIT 3;"

echo ""
echo "📍 REGIONAL BREAKDOWN"
sudo -u postgres psql -d sales_db -t -c "
SELECT '   ' || r.region_name || ': $' || TO_CHAR(SUM(f.total_amount), '999,999')
FROM warehouse.fact_sales f
JOIN warehouse.dim_regions r ON f.region_id = r.region_id
GROUP BY r.region_name
ORDER BY SUM(f.total_amount) DESC;"

echo ""
echo "=========================================="
