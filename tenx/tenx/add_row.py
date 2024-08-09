import pandas as pd

# Read the existing Parquet file into a DataFrame
df = pd.read_parquet(r"A:\pythonscrapyfiles\webscraping\tenx_2\tenx\tenx.parquet")

# Add a new field with the specified value
df['scraped_date'] = '20240726'

# Write the updated DataFrame back to a Parquet file
df.to_parquet('tenx_updated.parquet')