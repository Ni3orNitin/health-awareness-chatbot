import streamlit as st
import json
import random
import spacy
from rapidfuzz import fuzz
import requests
import mysql.connector
from mysql.connector import errorcode

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

st.set_page_config(page_title="Odisha Health Awareness Chatbot", page_icon="🩺")
st.title("🩺 Odisha Health Awareness Chatbot")

# MySQL database connection details
DB_CONFIG = {
    "host": "localhost",
    "user": "chatbot_user",  # <-- USE THE USERNAME YOU CREATED
    "passwd": "your_password",  # <-- USE THE PASSWORD YOU CREATED
    "database": "odisha_health_chatbot"
}

# Function to get intents from the database
def get_intents_from_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT tag, patterns, responses FROM intents")
        intents_data = cursor.fetchall()
        
        # Parse patterns and responses from JSON strings back into lists
        for intent in intents_data:
            intent['patterns'] = json.loads(intent['patterns'])
            intent['responses'] = json.loads(intent['responses'])
            
        return {"intents": intents_data}
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            st.error("Something is wrong with your username or password. Please check your credentials.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            st.error("Database does not exist. Please run the SQL script to create the database.")
        else:
            st.error(f"Error: {err}")
        return {"intents": []}
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Load intents from the database at the start
intents = get_intents_from_db()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Chatbot response logic with corrected Wikipedia fallback and logging ---
def get_response(user_input):
    user_input_lower = user_input.lower().strip()
    doc = nlp(user_input_lower)

    best_match = None
    best_score = 0
    chosen_response = None

    for intent in intents["intents"]:
        for pattern in intent["patterns"]:
            # Fuzzy string similarity
            score = fuzz.ratio(user_input_lower, pattern.lower())

            # Keyword overlap
            pattern_words = set(pattern.lower().split())
            input_words = set(user_input_lower.split())
            overlap = len(pattern_words & input_words)
            score += overlap * 10

            # Semantic similarity (SpaCy)
            pattern_doc = nlp(pattern.lower())
            similarity = doc.similarity(pattern_doc)
            score += similarity * 100

            if score > best_score:
                best_score = score
                chosen_response = random.choice(intent["responses"])

    # Threshold for intent match
    if best_score > 70:
        response_text = chosen_response
    else:
        # Wikipedia API fallback
        try:
            WIKI_API_URL = f"https://en.wikipedia.org/api/rest_v1/page/summary/{user_input_lower.replace(' ', '_')}"
            response = requests.get(WIKI_API_URL, timeout=5)
            if response.status_code == 200:
                data = response.json()
                extract = data.get("extract", "No detailed info found.")
                
                # Check for unhelpful Wikipedia pages
                if 'may refer to' in extract or 'The following is a list of' in extract:
                    response_text = "❌ I’m sorry, I don’t have information about that. Please consult a healthcare professional."
                else:
                    response_text = f"🌐 Wikipedia info about **{user_input.title()}**:\n\n{extract}"
            else:
                response_text = f"❌ Sorry, I don't have info about '{user_input}'. Please consult a healthcare professional."
        except requests.exceptions.RequestException:
            response_text = f"❌ Sorry, I couldn't fetch info for '{user_input}'. Please consult a healthcare professional."
            
    # Log the interaction to the database
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        sql = "INSERT INTO conversation_logs (user_input, chatbot_response) VALUES (%s, %s)"
        val = (user_input, response_text)
        cursor.execute(sql, val)
        conn.commit()
    except mysql.connector.Error as err:
        st.error(f"Error logging conversation: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

    return response_text

# --- Sidebar Quick Buttons ---
st.sidebar.title("⚡ Quick Questions")
if st.sidebar.button("🦟 Malaria Symptoms"):
    st.session_state.messages.append({"role": "user", "text": "What are malaria symptoms?"})
    response = get_response("What are malaria symptoms?")
    st.session_state.messages.append({"role": "bot", "text": response})

if st.sidebar.button("🦟 Malaria Precautions"):
    st.session_state.messages.append({"role": "user", "text": "How to prevent malaria?"})
    response = get_response("How to prevent malaria?")
    st.session_state.messages.append({"role": "bot", "text": response})

if st.sidebar.button("🩸 Dengue Symptoms"):
    st.session_state.messages.append({"role": "user", "text": "What are dengue symptoms?"})
    response = get_response("What are dengue symptoms?")
    st.session_state.messages.append({"role": "bot", "text": response})

if st.sidebar.button("🩸 Dengue Precautions"):
    st.session_state.messages.append({"role": "user", "text": "How to prevent dengue?"})
    response = get_response("How to prevent dengue?")
    st.session_state.messages.append({"role": "bot", "text": response})

if st.sidebar.button("🦠 COVID Symptoms"):
    st.session_state.messages.append({"role": "user", "text": "What are covid symptoms?"})
    response = get_response("What are covid symptoms?")
    st.session_state.messages.append({"role": "bot", "text": response})

if st.sidebar.button("🦠 COVID Precautions"):
    st.session_state.messages.append({"role": "user", "text": "What are covid precautions?"})
    response = get_response("What are covid precautions?")
    st.session_state.messages.append({"role": "bot", "text": response})

# --- Chat input box ---
user_input = st.chat_input("Ask me about Malaria 🦟, Dengue 🩸, or COVID 🦠 ...")

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