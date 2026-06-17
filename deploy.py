import pandas as pd
import os

print("=" * 70)
print("PREPARING DATA FOR TABLEAU")
print("=" * 70)

# >>> CREATE OUTPUT FOLDER
if not os.path.exists('output'):
    os.makedirs('output')
    print("\nCreated output/ folder")

# >>> COPY GENERATED CSVs
files_to_copy = [
    'financial_data.csv'
]

for file in files_to_copy:
    try:
        df = pd.read_csv(file)
        df.to_csv(f'output/{file}', index=False)
        print(f"\nCopied: {file} -> output/{file}")
        print(f"   Rows: {len(df):,}")
        print(f"   Columns: {len(df.columns)}")
    except FileNotFoundError:
        print(f"\nWarning: {file} not found")

# >>> VERIFY OUTPUT FOLDER
print("\n" + "=" * 70)
print("OUTPUT FOLDER CONTENTS")
print("=" * 70)

output_files = os.listdir('output') if os.path.exists('output') else []
output_files.sort()

print(f"\nTotal files: {len(output_files)}")
for file in output_files:
    file_path = f'output/{file}'
    file_size = os.path.getsize(file_path) / 1024
    print(f"   {file} ({file_size:.1f} KB)")

print("\n" + "=" * 70)
print("READY FOR TABLEAU")
print("=" * 70)
print("\nTo import to Tableau Public:")
print("   1. Go to https://public.tableau.com")
print("   2. Create account (if needed)")
print("   3. Click 'Create' -> 'Data Source'")
print("   4. Upload CSV files from output/ folder")
print("   5. Build your dashboard")