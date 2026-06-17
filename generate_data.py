import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3

# ============================================================================
# STEP 1: SET RANDOM SEED (For reproducible data)
# ============================================================================
# This ensures every time you run this script, you get the SAME fake data
# (useful for testing, so you don't worry about randomness)

np.random.seed(42)

print("=" * 70)
print("GENERATING SYNTHETIC SaaS FINANCIAL DATA")
print("=" * 70)

# ============================================================================
# STEP 2: DEFINE YOUR BUSINESS PARAMETERS
# ============================================================================
# These are the "dimensions" of your fake company

products = ['Basic', 'Pro', 'Enterprise', 'API', 'Analytics', 'Support', 'Training', 'Premium', 'Custom', 'Legacy']
# 10 products at different price tiers

regions = ['AMER', 'EMEA', 'APAC', 'LATAM', 'INDIA']
# 5 geographic regions

segments = ['Startup', 'SMB', 'Mid-Market', 'Enterprise']
# 4 customer segments by company size

# ============================================================================
# STEP 3: CREATE TIME RANGE
# ============================================================================
# Start date: January 2023
# End date: December 2024 (24 months of data)

start_date = datetime(2023, 1, 1)
n_months = 24

print(f"\n📅 Creating data from {start_date.strftime('%B %Y')} for {n_months} months")
print(f"   (Jan 2023 → Dec 2024)")

# ============================================================================
# STEP 4: GENERATE FINANCIAL RECORDS
# ============================================================================
# This is the MAIN LOOP that creates all your data

records = []

# Loop through each month
for month in range(n_months):
    # Calculate the current month's date
    current_date = start_date + timedelta(days=30 * month)
    year_month = current_date.strftime('%Y-%m')
    
    print(f"   Generating {year_month}...", end=" ")
    
    # For each month, create records for EVERY product × region × segment combo
    for product in products:
        for region in regions:
            for segment in segments:
                
                # ============================================================
                # REVENUE CALCULATION (with growth + seasonality)
                # ============================================================
                
                # Base revenue: random starting point ($50K - $500K)
                base_revenue = np.random.uniform(50000, 500000)
                
                # Growth factor: 2% month-over-month growth
                # Formula: 1.02 ^ month
                # Month 0: 1.02^0 = 1.0x (baseline)
                # Month 6: 1.02^6 = 1.126x (12.6% growth)
                # Month 12: 1.02^12 = 1.268x (26.8% growth after 1 year)
                growth_factor = 1.02 ** month
                
                # Seasonality: 10% variation (peak in month 12, dip in month 6)
                # Formula: 1 + 0.1 * sin(2π * month / 12)
                # This creates a wave pattern that repeats every 12 months
                # Max: 1.1x (10% boost in peak season)
                # Min: 0.9x (10% drop in low season)
                seasonality = 1 + 0.1 * np.sin(2 * np.pi * month / 12)
                
                # Final revenue = base × growth × seasonality
                revenue = base_revenue * growth_factor * seasonality
                
                # ============================================================
                # COST OF GOODS SOLD (COGS)
                # ============================================================
                # What it costs to deliver the product
                # In SaaS, typically servers, payment processing, support staff
                # Normal range: 30-40% of revenue
                
                cogs_ratio = np.random.uniform(0.30, 0.40)
                cogs = revenue * cogs_ratio
                
                # ============================================================
                # OPERATING EXPENSES (OpEx)
                # ============================================================
                # Overhead: salaries, rent, marketing, software licenses
                # Normal range: 20-30% of revenue
                
                opex_ratio = np.random.uniform(0.20, 0.30)
                opex = revenue * opex_ratio
                
                # ============================================================
                # PROFIT CALCULATIONS
                # ============================================================
                
                # Gross Profit = Revenue - COGS
                gross_profit = revenue - cogs
                
                # Operating Income = Gross Profit - OpEx
                operating_income = gross_profit - opex
                
                # ============================================================
                # CUSTOMER COUNTS (For ARR/MRR calculations)
                # ============================================================
                
                # Total customers (varies by product)
                n_customers = np.random.randint(10, 500)
                
                # Of these, what % are active subscriptions?
                active_pct = np.random.uniform(0.70, 0.95)
                active = int(n_customers * active_pct)
                
                # Churn (customers who left)
                churn_pct = np.random.uniform(0.05, 0.15)
                churned = int(n_customers * churn_pct)
                
                # New customers this month
                new_pct = np.random.uniform(0.10, 0.30)
                new = int(n_customers * new_pct)
                
                # ============================================================
                # SUBSCRIPTION STATUS (For MRR calculation)
                # ============================================================
                
                # Each customer has a status: active, churned, or new
                subscription_status = np.random.choice(
                    ['active', 'churned', 'new'],
                    p=[0.75, 0.15, 0.10]  # 75% active, 15% churned, 10% new
                )
                
                # Revenue type: subscription (recurring) or one-time (one-off)
                revenue_type = np.random.choice(
                    ['subscription', 'one_time'],
                    p=[0.80, 0.20]  # 80% recurring, 20% one-time
                )
                
                # ============================================================
                # CREATE THE RECORD
                # ============================================================
                # This is one row of data for your database
                
                record = {
                    'year_month': year_month,                          # e.g., "2023-01"
                    'date': current_date.date(),                       # e.g., 2023-01-01
                    'product': product,                                # e.g., "Pro"
                    'region': region,                                  # e.g., "AMER"
                    'customer_segment': segment,                       # e.g., "SMB"
                    'customer_id': f"{product}_{region}_{segment}_{month}",  # Unique ID
                    'revenue': round(revenue, 2),                      # Round to 2 decimals
                    'cogs': round(cogs, 2),
                    'opex': round(opex, 2),
                    'gross_profit': round(gross_profit, 2),
                    'operating_income': round(operating_income, 2),
                    'n_customers': n_customers,
                    'active_subscriptions': active,
                    'churned_count': churned,
                    'new_subscriptions': new,
                    'subscription_status': subscription_status,
                    'revenue_type': revenue_type
                }
                
                records.append(record)
    
    print("✓")

# ============================================================================
# STEP 5: CREATE PANDAS DATAFRAME
# ============================================================================
# Convert list of dictionaries to a DataFrame (table format)

df = pd.DataFrame(records)

print(f"\n Generated {len(df):,} financial records")
print(f"   {len(df) / n_months:.0f} records per month")
print(f"   {df['product'].nunique()} products")
print(f"   {df['region'].nunique()} regions")
print(f"   {df['customer_segment'].nunique()} segments")

# ============================================================================
# STEP 6: CALCULATE SUMMARY STATISTICS
# ============================================================================
# Show what the data looks like

print(f"\n FINANCIAL SUMMARY:")
print(f"   Total Revenue (all {n_months} months): ${df['revenue'].sum():,.0f}")
print(f"   Avg Monthly Revenue: ${df.groupby('year_month')['revenue'].sum().mean():,.0f}")
print(f"   Avg Gross Margin %: {((df['gross_profit'] / df['revenue'] * 100).mean()):,.1f}%")
print(f"   Avg Operating Margin %: {((df['operating_income'] / df['revenue'] * 100).mean()):,.1f}%")

# ============================================================================
# STEP 7: SAVE TO CSV
# ============================================================================
# Export the data so we can inspect it and use it later

df.to_csv('financial_data.csv', index=False)
print(f"\n Saved to: financial_data.csv ({len(df):,} rows)")

# ============================================================================
# STEP 8: CREATE SQLITE DATABASE
# ============================================================================
# SQLite is a lightweight database that stores data locally

conn = sqlite3.connect('financial_analytics.db')
df.to_sql('financial_data', conn, if_exists='replace', index=False)
print(f"Saved to: financial_analytics.db")

# ============================================================================
# STEP 9: VERIFY DATA IN DATABASE
# ============================================================================
# Query the database to confirm data was saved correctly

query = """
SELECT 
    year_month,
    COUNT(*) as record_count,
    ROUND(SUM(revenue), 2) as total_revenue,
    ROUND(AVG(revenue), 2) as avg_revenue
FROM financial_data
GROUP BY year_month
ORDER BY year_month
LIMIT 5
"""

print(f"\n Sample from database (first 5 months):")
sample = pd.read_sql_query(query, conn)
print(sample.to_string(index=False))

# ============================================================================
# STEP 10: CLOSE DATABASE CONNECTION
# ============================================================================

conn.close()

print("\n" + "=" * 70)
print(" DATA GENERATION COMPLETE!")
print("=" * 70)

