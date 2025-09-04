-- Drop the database if it already exists to ensure a clean start
DROP DATABASE IF EXISTS odisha_health_chatbot;

-- Create the new database
CREATE DATABASE odisha_health_chatbot;

-- Use the new database
USE odisha_health_chatbot;

-- Create the diseases table
CREATE TABLE diseases (
    disease_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

-- Create the intents table
CREATE TABLE intents (
    intent_id INT AUTO_INCREMENT PRIMARY KEY,
    disease_id INT,
    tag VARCHAR(255) NOT NULL,
    patterns TEXT NOT NULL,
    responses TEXT NOT NULL,
    FOREIGN KEY (disease_id) REFERENCES diseases(disease_id)
);

-- Create the table for conversation logs
CREATE TABLE conversation_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_input TEXT NOT NULL,
    chatbot_response TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert data into the diseases table
INSERT INTO diseases (name) VALUES
('Malaria'),
('Dengue'),
('COVID'),
('NITIN'); -- <-- 'NITIN' is now correctly added here

-- Insert data into the intents table, linking to the diseases
INSERT INTO intents (disease_id, tag, patterns, responses) VALUES
((SELECT disease_id FROM diseases WHERE name = 'Malaria'), 'malaria_precautions', '["How to prevent malaria?", "Precautions for malaria", "How can I stay safe from malaria?"]', '["🦟 To prevent **Malaria**: Use mosquito nets, apply insect repellent, wear long-sleeved clothes, and keep surroundings clean."]')
,
((SELECT disease_id FROM diseases WHERE name = 'Malaria'), 'malaria_symptoms', '["What are malaria symptoms?", "Signs of malaria", "Symptoms of malaria"]', '["🦟 Common **Malaria** symptoms: High fever, chills, sweating, headache, nausea, and muscle pain."]')
,
((SELECT disease_id FROM diseases WHERE name = 'Dengue'), 'dengue_precautions', '["How to prevent dengue?", "Precautions for dengue", "How can I stay safe from dengue?"]', '["🩸 To prevent **Dengue**: Remove stagnant water, use mosquito repellents, cover water containers, and sleep under mosquito nets."]')
,
((SELECT disease_id FROM diseases WHERE name = 'Dengue'), 'dengue_symptoms', '["What are dengue symptoms?", "Signs of dengue", "Symptoms of dengue"]', '["🩸 **Dengue** symptoms include: Sudden fever, severe headache, pain behind eyes, joint/muscle pain, skin rash, and mild bleeding (like gums/nose)."]'),
((SELECT disease_id FROM diseases WHERE name = 'COVID'), 'covid_precautions', '["What are covid precautions?", "How to prevent coronavirus?", "Precautions for covid", "How can I stay safe from covid?", "Ways to avoid covid"]', '["🦠 **COVID-19 Precautions**: Wash hands frequently, wear a mask 😷, maintain social distancing ↔️, get vaccinated 💉, and stay in well-ventilated areas."]')
,
((SELECT disease_id FROM diseases WHERE name = 'COVID'), 'covid_symptoms', '["What are covid symptoms?", "Signs of coronavirus", "How do I know if I have covid?"]', '["🦠 **COVID-19 Symptoms**: Fever 🤒, dry cough 😮💨, tiredness, loss of taste/smell 👃, and difficulty breathing. Please consult a doctor if symptoms persist."]')
,
((SELECT disease_id FROM diseases WHERE name = 'NITIN'), 'nitin_precautions', '["What are nitin precautions?", "How to prevent nitin?", "Precautions for nitin", "How can I stay safe from nitin?", "Ways to avoid nitin"]', '["🦠 **NITIN Precautions**: Wash hands frequently, wear a mask 😷, maintain social distancing ↔️, get vaccinated 💉, and stay in well-ventilated areas."]')
,
((SELECT disease_id FROM diseases WHERE name = 'NITIN'), 'nitin_symptoms', '["What are nitin symptoms?", "Signs of nitin", "How do I know if I have nitin?"]', '["NITIN Symptoms: lucky you are , you are love with nitin ❤️, best moment ever, best human, smart boy. Contanct him at 6207367883."]');
