import streamlit as st
import json
import random
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Load intents from data.json
with open("data.json", "r") as f:
    intents = json.load(f)

st.set_page_config(page_title="Odisha Health Awareness Chatbot", page_icon="🩺")
st.title("🩺 Odisha Health Awareness Chatbot")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

def get_response(user_input):
    user_input = user_input.lower()
    for intent in intents["intents"]:
        for pattern in intent["patterns"]:
            if pattern.lower() in user_input:
                return random.choice(intent["responses"])
    return "❌ I’m sorry, I don’t have information about that. Please consult a healthcare professional."

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
