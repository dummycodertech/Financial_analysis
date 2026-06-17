import pandas as pd
import sqlite3
from prophet import Prophet
import warnings

warnings.filterwarnings('ignore')

conn = sqlite3.connect('financial_analytics.db')

print("=" * 70)
print("REVENUE FORECASTING - PROPHET")
print("=" * 70)

# >>> PREPARE DATA FOR PROPHET
query = """
SELECT
    date,
    SUM(revenue) AS total_revenue
FROM financial_data
GROUP BY date
ORDER BY date
"""

df = pd.read_sql_query(query, conn)
df['date'] = pd.to_datetime(df['date'])

print(f"\nHistorical data: {len(df)} days")
print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")

# >>> FORMAT FOR PROPHET
prophet_df = df.rename(columns={'date': 'ds', 'total_revenue': 'y'})

# >>> FIT MODEL
print("\nFitting Prophet model...")
model = Prophet(yearly_seasonality=True, seasonality_mode='multiplicative')
model.fit(prophet_df)

# >>> CREATE FORECAST
print("Generating 6-month forecast...")
future = model.make_future_dataframe(periods=180, freq='D')
forecast = model.predict(future)

# >>> EXTRACT FORECAST DATA
forecast_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(180)
forecast_data.columns = ['date', 'forecast', 'lower_bound', 'upper_bound']
forecast_data['forecast_type'] = 'Forecast'

historical_data = df.copy()
historical_data['forecast'] = None
historical_data['lower_bound'] = None
historical_data['upper_bound'] = None
historical_data['forecast_type'] = 'Historical'

combined = pd.concat([historical_data, forecast_data], ignore_index=True)

# >>> MONTHLY AGGREGATION FOR TABLEAU
monthly_forecast = forecast_data.copy()
monthly_forecast['date'] = pd.to_datetime(monthly_forecast['date'])
monthly_forecast['year_month'] = monthly_forecast['date'].dt.strftime('%Y-%m')

monthly_summary = monthly_forecast.groupby('year_month').agg({
    'forecast': 'sum',
    'lower_bound': 'sum',
    'upper_bound': 'sum'
}).round(2).reset_index()

print("\n6-MONTH REVENUE FORECAST:")
print("-" * 70)
print(monthly_summary.to_string(index=False))

# >>> SAVE OUTPUTS
monthly_summary.to_csv('output/revenue_forecast.csv', index=False)
combined.to_csv('output/forecast_with_history.csv', index=False)

print("\nSaved to:")
print("   - output/revenue_forecast.csv")
print("   - output/forecast_with_history.csv")

# >>> FORECAST STATISTICS
print("\n" + "=" * 70)
print("FORECAST SUMMARY")
print("=" * 70)

latest_actual = df['total_revenue'].iloc[-1]
forecast_next_6m = monthly_summary['forecast'].sum()
growth_rate = ((forecast_next_6m / (latest_actual * 6)) - 1) * 100

print(f"\nLast actual daily revenue: ${latest_actual:,.2f}")
print(f"6-month forecast total: ${forecast_next_6m:,.2f}")
print(f"Implied daily growth rate: {growth_rate:.1f}%")
print(f"Average daily forecast: ${forecast_next_6m / 180:,.2f}")

conn.close()

print("\n" + "=" * 70)
print("FORECASTING COMPLETE")
print("=" * 70)