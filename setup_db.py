import sqlite3
import pandas as pd

# Connect to sqlite (creates health.db if not exists)
conn = sqlite3.connect("health.db")
cursor = conn.cursor()

# Create a single, comprehensive diseases table
cursor.execute("""
CREATE TABLE IF NOT EXISTS diseases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    symptoms TEXT,
    precaution_1 TEXT,
    precaution_2 TEXT,
    precaution_3 TEXT,
    precaution_4 TEXT
)
""")

try:
    # Read both CSV files into pandas DataFrames
    symptoms_df = pd.read_csv("DiseaseAndSymptoms.csv")
    precaution_df = pd.read_csv("Disease precaution.csv")
    
    # Correctly handle the symptom columns
    symptoms_cols = ['Symptom_' + str(i) for i in range(1, 18)]
    symptoms_df['symptoms'] = symptoms_df[symptoms_cols].astype(str).agg(', '.join, axis=1)
    symptoms_df = symptoms_df[['Disease', 'symptoms']]
    symptoms_df.rename(columns={'Disease': 'name'}, inplace=True)
    
    # Correctly handle the precaution columns
    precaution_df.columns = ['name', 'precaution_1', 'precaution_2', 'precaution_3', 'precaution_4']

    # Merge the two DataFrames on the 'name' column
    combined_df = pd.merge(symptoms_df, precaution_df, on='name', how='left')
    print(combined_df.head())
    
    # Insert the combined data into the database
    combined_df.to_sql('diseases', conn, if_exists='replace', index=False)
    
except Exception as e:
    print(f"Error importing data from CSV: {e}")
    
conn.commit()
conn.close()

print("Database 'health.db' created and populated successfully.")