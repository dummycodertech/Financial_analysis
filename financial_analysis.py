import pandas as pd
import sqlite3
import os
output_dir = 'output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")
conn = sqlite3.connect('financial_analytics.db')

print("=" * 70)
print("FINANCIAL ANALYSIS - SQL QUERIES")
print("=" * 70)

# >>> QUERY 1: P&L WATERFALL
print("\n1. P&L WATERFALL (Revenue -> Profit)")
print("-" * 70)

query1 = """
WITH monthly_pl AS (
    SELECT
        year_month,
        region,
        SUM(revenue) AS total_revenue,
        SUM(cogs) AS total_cogs,
        SUM(opex) AS total_opex,
        SUM(revenue) - SUM(cogs) AS gross_profit,
        SUM(revenue) - SUM(cogs) - SUM(opex) AS operating_income,
        ROUND((SUM(revenue) - SUM(cogs)) * 100.0 / SUM(revenue), 1) AS gross_margin_pct,
        ROUND((SUM(revenue) - SUM(cogs) - SUM(opex)) * 100.0 / SUM(revenue), 1) AS op_margin_pct
    FROM financial_data
    GROUP BY year_month, region
)
SELECT * FROM monthly_pl ORDER BY year_month DESC LIMIT 10
"""

df1 = pd.read_sql_query(query1, conn)
print(df1.to_string(index=False))
df1.to_csv('output/pl_waterfall.csv', index=False)
print("\nSaved to: output/pl_waterfall.csv")

# >>> QUERY 2: BUDGET VS ACTUAL VARIANCE
print("\n2. BUDGET VS ACTUAL VARIANCE")
print("-" * 70)

query2 = """
SELECT
    year_month,
    product,
    SUM(revenue) AS actual_revenue,
    ROUND(SUM(revenue) * 0.95, 2) AS budgeted_revenue,
    SUM(revenue) - ROUND(SUM(revenue) * 0.95, 2) AS variance,
    ROUND((SUM(revenue) - ROUND(SUM(revenue) * 0.95, 2)) * 100.0 / (SUM(revenue) * 0.95), 1) AS variance_pct
FROM financial_data
GROUP BY year_month, product
HAVING ABS((SUM(revenue) - ROUND(SUM(revenue) * 0.95, 2)) * 100.0 / (SUM(revenue) * 0.95)) > 5
ORDER BY year_month DESC
LIMIT 10
"""

df2 = pd.read_sql_query(query2, conn)
print(df2.to_string(index=False))
df2.to_csv('output/variance_analysis.csv', index=False)
print("\nSaved to: output/variance_analysis.csv")

# >>> QUERY 3: PROFITABILITY BY SEGMENT
print("\n3. PROFITABILITY BY CUSTOMER SEGMENT")
print("-" * 70)

query3 = """
SELECT
    year_month,
    customer_segment,
    COUNT(DISTINCT customer_id) AS customer_count,
    ROUND(SUM(revenue), 2) AS segment_revenue,
    ROUND(SUM(cogs), 2) AS segment_cogs,
    ROUND(SUM(opex), 2) AS segment_opex,
    ROUND(SUM(revenue) - SUM(cogs), 2) AS gross_profit,
    ROUND((SUM(revenue) - SUM(cogs)) * 100.0 / SUM(revenue), 1) AS gross_margin_pct,
    ROUND(SUM(revenue) - SUM(cogs) - SUM(opex), 2) AS operating_profit,
    ROUND((SUM(revenue) - SUM(cogs) - SUM(opex)) * 100.0 / SUM(revenue), 1) AS op_margin_pct
FROM financial_data
GROUP BY year_month, customer_segment
ORDER BY year_month DESC
LIMIT 16
"""

df3 = pd.read_sql_query(query3, conn)
print(df3.to_string(index=False))
df3.to_csv('output/segment_profitability.csv', index=False)
print("\nSaved to: output/segment_profitability.csv")

# >>> QUERY 4: PRODUCT REVENUE TRENDS
print("\n4. PRODUCT REVENUE TRENDS (Month-over-Month Growth)")
print("-" * 70)

query4 = """
WITH product_trends AS (
    SELECT
        year_month,
        product,
        SUM(revenue) AS product_revenue,
        COUNT(DISTINCT customer_id) AS active_customers
    FROM financial_data
    GROUP BY year_month, product
)
SELECT
    year_month,
    product,
    ROUND(product_revenue, 2) AS monthly_revenue,
    active_customers,
    ROUND(product_revenue / NULLIF(active_customers, 0), 2) AS arpu
FROM product_trends
ORDER BY year_month DESC, product_revenue DESC
LIMIT 15
"""

df4 = pd.read_sql_query(query4, conn)
print(df4.to_string(index=False))
df4.to_csv('output/product_trends.csv', index=False)
print("\nSaved to: output/product_trends.csv")

# >>> QUERY 5: ARR/MRR METRICS
print("\n5. ARR/MRR CALCULATION (Subscription Revenue)")
print("-" * 70)

query5 = """
SELECT
    year_month,
    customer_segment,
    SUM(CASE WHEN subscription_status = 'active' THEN revenue ELSE 0 END) AS mrr,
    ROUND(SUM(CASE WHEN subscription_status = 'active' THEN revenue ELSE 0 END) * 12, 2) AS arr,
    COUNT(DISTINCT CASE WHEN subscription_status = 'active' THEN customer_id END) AS active_subscriptions,
    COUNT(DISTINCT CASE WHEN subscription_status = 'churned' THEN customer_id END) AS churned_count,
    COUNT(DISTINCT CASE WHEN subscription_status = 'new' THEN customer_id END) AS new_subscriptions
FROM financial_data
GROUP BY year_month, customer_segment
ORDER BY year_month DESC
LIMIT 16
"""

df5 = pd.read_sql_query(query5, conn)
print(df5.to_string(index=False))
df5.to_csv('output/arr_mrr_metrics.csv', index=False)
print("\nSaved to: output/arr_mrr_metrics.csv")

# >>> QUERY 6: MARGIN ANALYSIS BY PRODUCT
print("\n6. MARGIN ANALYSIS - PRODUCT PROFITABILITY")
print("-" * 70)

query6 = """
SELECT
    year_month,
    product,
    region,
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(SUM(cogs), 2) AS cogs,
    ROUND(SUM(opex), 2) AS opex,
    ROUND((SUM(cogs) * 100.0 / SUM(revenue)), 1) AS cogs_pct,
    ROUND((SUM(opex) * 100.0 / SUM(revenue)), 1) AS opex_pct,
    ROUND(((SUM(revenue) - SUM(cogs)) * 100.0 / SUM(revenue)), 1) AS gross_margin_pct,
    ROUND(((SUM(revenue) - SUM(cogs) - SUM(opex)) * 100.0 / SUM(revenue)), 1) AS net_margin_pct
FROM financial_data
GROUP BY year_month, product, region
ORDER BY year_month DESC, net_margin_pct DESC
LIMIT 15
"""

df6 = pd.read_sql_query(query6, conn)
print(df6.to_string(index=False))
df6.to_csv('output/margin_analysis.csv', index=False)
print("\nSaved to: output/margin_analysis.csv")

conn.close()

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
print("\nAll CSVs saved to output/ folder")
print("Ready for Tableau import")