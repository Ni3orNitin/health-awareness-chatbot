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
def download_spacy_model():
    model_name = "en_core_web_sm"
    try:
        spacy.load(model_name)
    except OSError:
        subprocess.run([sys.executable, "-m", "spacy", "download", model_name])
        
    try:
        model_path = os.path.join(spacy.util.get_data_path(), model_name)
        if not os.path.exists(model_path):
            shutil.copytree(
                os.path.join(sys.prefix, "share", "spacy", model_name),
                model_path
            )
    except Exception as e:
        st.error(f"Error while linking model: {e}")
        st.stop()

download_spacy_model()
nlp = spacy.load("en_core_web_sm")

st.set_page_config(page_title="Odisha Health Awareness Chatbot", page_icon="🩺")
st.title("🩺 Odisha Health Awareness Chatbot (SQLite Edition)")

# --- Database connection helper ---
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
            name, symptoms, treatment, side_effects = disease_data
            
            # Use Spacy to check for specific intents
            doc = nlp(user_input_lower)
            if any(token.text in ["symptom", "symptoms"] for token in doc):
                return f"🦠 Symptoms of **{name}**: {symptoms}"
            elif any(token.text in ["treatment", "treat"] for token in doc):
                return f"💊 Treatment for **{name}**: {treatment}"
            elif any(token.text in ["side effect", "side effects"] for token in doc):
                return f"⚠️ Side effects of treatment for **{name}**: {side_effects}"
            else:
                return (
                    f"ℹ️ Info about **{name}**:\n\n"
                    f"- **Symptoms**: {symptoms}\n"
                    f"- **Treatment**: {treatment}\n"
                    f"- **Side Effects**: {side_effects}"
                )

    # ... The rest of your code for Wikipedia fallback and final fallback ...
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

if st.sidebar.button("🦟 Malaria Treatment"):
    st.session_state.messages.append({"role": "user", "text": "How to treat malaria?"})
    response = get_response("How to treat malaria?")
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