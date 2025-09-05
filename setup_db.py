import sqlite3

conn = sqlite3.connect("health.db")
cursor = conn.cursor()

# Create diseases table
cursor.execute("""
CREATE TABLE IF NOT EXISTS diseases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    symptoms TEXT,
    treatment TEXT,
    side_effects TEXT
)
""")

# Insert sample data
cursor.execute("""
INSERT OR IGNORE INTO diseases (name, symptoms, treatment, side_effects)
VALUES
('Malaria', 'Fever, chills, headache', 'Antimalarial drugs', 'Nausea, dizziness'),
('Diabetes', 'Increased thirst, frequent urination', 'Insulin, lifestyle changes', 'Low blood sugar, fatigue')
""")

conn.commit()
conn.close()

print("Database 'health.db' created and populated successfully.")