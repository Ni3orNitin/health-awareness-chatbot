import streamlit as st
import sqlite3
import spacy
import random
from rapidfuzz import fuzz
import requests

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

st.set_page_config(page_title="Odisha Health Awareness Chatbot", page_icon="🩺")
st.title("🩺 Odisha Health Awareness Chatbot (SQLite Edition)")

# --- Database connection helper ---
def get_connection():
    return sqlite3.connect("health.db")

# --- Query DB for disease info ---
def get_disease_info(disease_name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, symptoms, treatment, side_effects FROM diseases WHERE LOWER(name)=?", (disease_name.lower(),))
    row = cursor.fetchone()
    conn.close()
    return row

# --- Chatbot response logic ---
def get_response(user_input):
    user_input_lower = user_input.lower().strip()
    doc = nlp(user_input_lower)

    # Check if input mentions a disease
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM diseases")
    all_diseases = [row[0] for row in cursor.fetchall()]
    conn.close()

    best_match = None
    best_score = 0
    for disease in all_diseases:
        score = fuzz.ratio(user_input_lower, disease.lower())
        if score > best_score:
            best_score = score
            best_match = disease

    if best_match and best_score > 70:
        disease_data = get_disease_info(best_match)
        if disease_data:
            name, symptoms, treatment, side_effects = disease_data
            if "symptom" in user_input_lower:
                return f"🦠 Symptoms of **{name}**: {symptoms}"
            elif "treatment" in user_input_lower:
                return f"💊 Treatment for **{name}**: {treatment}"
            elif "side effect" in user_input_lower:
                return f"⚠️ Side effects of treatment for **{name}**: {side_effects}"
            else:
                return f"ℹ️ Info about **{name}**:\n- Symptoms: {symptoms}\n- Treatment: {treatment}\n- Side Effects: {side_effects}"

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
    st.session_state.messages.append({"role": "bot", "text": response})

if st.sidebar.button("🦟 Malaria Treatment"):
    st.session_state.messages.append({"role": "user", "text": "How to treat malaria?"})
    response = get_response("How to treat malaria?")
    st.session_state.messages.append({"role": "bot", "text": response})

if st.sidebar.button("🩸 Diabetes Symptoms"):
    st.session_state.messages.append({"role": "user", "text": "What are diabetes symptoms?"})
    response = get_response("What are diabetes symptoms?")
    st.session_state.messages.append({"role": "bot", "text": response})

# --- Chat input box ---
user_input = st.chat_input("Ask me about Malaria, Diabetes or other diseases...")

if user_input:
    st.session_state.messages.append({"role": "user", "text": user_input})
    response = get_response(user_input)
    st.session_state.messages.append({"role": "bot", "text": response})

# --- Chat history display ---
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div style='text-align: left; padding:8px; background:#DCF8C6; border-radius:10px; margin:5px; display:inline-block;'>{msg['text']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align: right; padding:8px; background:#E6E6FA; border-radius:10px; margin:5px; display:inline-block;'>{msg['text']}</div>", unsafe_allow_html=True)
