import sqlite3
import pandas as pd

# Connect to sqlite (creates health.db if not exists)
conn = sqlite3.connect("health.db")
cursor = conn.cursor()

# Drop existing table (so we start fresh with correct schema)
cursor.execute("DROP TABLE IF EXISTS diseases")

# Create diseases table with id
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
    # Read CSV files
    symptoms_df = pd.read_csv("DiseaseAndSymptoms.csv")
    precaution_df = pd.read_csv("Disease precaution.csv")

    # Identify symptom columns
    symptom_cols = [col for col in symptoms_df.columns if col.startswith("Symptom")]

    # Combine all symptom columns into one string
    symptoms_df["symptoms"] = symptoms_df[symptom_cols].apply(
        lambda x: ", ".join(x.dropna().astype(str)), axis=1
    )

    # Keep only Disease + combined symptoms
    symptoms_df = symptoms_df.rename(columns={"Disease": "name"})[["name", "symptoms"]]

    # Rename precaution columns
    precaution_df.columns = ["name", "precaution_1", "precaution_2", "precaution_3", "precaution_4"]

    # Merge datasets
    combined_df = pd.merge(symptoms_df, precaution_df, on="name", how="left")

    # Insert into existing table (append mode, keeps schema with id)
    combined_df.to_sql("diseases", conn, if_exists="append", index=False)

    # Preview first 5 rows in terminal
    print("\nPreview of merged data:")
    print(combined_df.head())

except Exception as e:
    print(f"Error importing data from CSV: {e}")

conn.commit()
conn.close()

print("\nDatabase 'health.db' created and populated successfully with autoincrement id.")
