import streamlit as st
import sqlite3
import spacy
import random
from rapidfuzz import fuzz
import requests
import os
import shutil
import subprocess
import sys

# --- Spacy Model Setup ---
# This function ensures the model is downloaded for deployment.
@st.cache_resource
def load_spacy_model():
    model_name = "en_core_web_sm"
    try:
        nlp = spacy.load(model_name)
    except OSError:
        # If the model is not found, install it directly from the URL
        st.info("SpaCy model not found. Downloading the model...")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl"
            ],
            check=True
        )
        nlp = spacy.load(model_name)
    return nlp

nlp = load_spacy_model()

st.set_page_config(page_title="Odisha Health Awareness Chatbot", page_icon="🩺")
st.title("🩺 Odisha Health Awareness Chatbot (SQLite Edition)")

# --- Database connection helper ---
def get_connection():
    return sqlite3.connect("health.db")

# --- Query DB for disease info ---
def get_disease_info(disease_name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, symptoms, precaution_1, precaution_2, precaution_3, precaution_4 FROM diseases WHERE LOWER(name)=?", (disease_name.lower(),))
    row = cursor.fetchone()
    conn.close()
    return row

# --- Chatbot response logic ---
def get_response(user_input):
    user_input_lower = user_input.lower().strip()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM diseases")
    all_diseases = [row[0] for row in cursor.fetchall()]
    conn.close()

    best_match = None
    best_score = 0
    
    # Iterate through each word in the user's input to find a match
    for word in user_input_lower.split():
        for disease in all_diseases:
            # Check for a high fuzzy ratio score for a single word
            score = fuzz.ratio(word, disease.lower())
            if score > best_score:
                best_score = score
                best_match = disease

    if best_match and best_score > 70:
        disease_data = get_disease_info(best_match)
        if disease_data:
            name, symptoms, precaution_1, precaution_2, precaution_3, precaution_4 = disease_data
            
            # Use Spacy to check for specific intents
            doc = nlp(user_input_lower)
            if any(token.text in ["symptom", "symptoms"] for token in doc):
                return f"🦠 Symptoms of **{name}**: {symptoms}"
            elif any(token.text in ["precaution", "prevent", "prevention"] for token in doc):
                return (
                    f"💊 Precautions for **{name}**:\n\n"
                    f"- {precaution_1}\n"
                    f"- {precaution_2}\n"
                    f"- {precaution_3}\n"
                    f"- {precaution_4}"
                )
            else:
                return (
                    f"ℹ️ Info about **{name}**:\n\n"
                    f"- **Symptoms**: {symptoms}\n"
                    f"- **Precautions**: {precaution_1}, {precaution_2}, {precaution_3}, {precaution_4}"
                )
    
    # Wikipedia fallback
    try:
        WIKI_API_URL = f"https://en.wikipedia.org/api/rest_v1/page/summary/{user_input_lower.replace(' ', '_')}"
        response = requests.get(WIKI_API_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            extract = data.get("extract", "No detailed info found.")
            if 'may refer to' in extract or 'The following is a list of' in extract:
                return "❌ Sorry, I don’t have detailed info. Please consult a healthcare professional."
            else:
                return f"🌐 Wikipedia info about **{user_input.title()}**:\n\n{extract}"
    except requests.exceptions.RequestException:
        pass
    
    return f"❌ Sorry, I don’t have information about '{user_input}'. Please consult a healthcare professional."

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar Quick Buttons ---
st.sidebar.title("⚡ Quick Questions")
if st.sidebar.button("🦟 Malaria Symptoms"):
    st.session_state.messages.append({"role": "user", "text": "What are malaria symptoms?"})
    response = get_response("What are malaria symptoms?")
    st.session_state.messages.append({"role": "assistant", "text": response})

if st.sidebar.button("🩸 Diabetes Symptoms"):
    st.session_state.messages.append({"role": "user", "text": "What are diabetes symptoms?"})
    response = get_response("What are diabetes symptoms?")
    st.session_state.messages.append({"role": "assistant", "text": response})

# --- Chat input box ---
user_input = st.chat_input("Ask me about Malaria, Diabetes or other diseases...")

if user_input:
    st.session_state.messages.append({"role": "user", "text": user_input})
    response = get_response(user_input)
    st.session_state.messages.append({"role": "assistant", "text": response})

# --- Chat history display ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["text"])