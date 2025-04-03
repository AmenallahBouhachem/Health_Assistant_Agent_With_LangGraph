import pandas as pd
import sqlite3

csv_file = 'healthcare.csv'
df = pd.read_csv(csv_file)

db_file = 'healthcare.db'
conn = sqlite3.connect(db_file)
df.to_sql('HEALTH', conn, index=False, if_exists='replace')

conn.close()