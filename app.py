import streamlit as st
import json
import random
import spacy

# --- Page Config ---
st.set_page_config(page_title="Odisha Health Awareness Chatbot")

st.title("👨‍⚕️ Odisha Health Awareness Chatbot")
st.markdown("Hi! I'm your virtual health assistant. Ask me anything about disease symptoms, prevention, or vaccination schedules.")

# --- Load SpaCy Model ---
try:
    nlp = spacy.load("en_core_web_sm")
    st.success("SpaCy model loaded successfully! ✅")
except Exception as e:
    st.error(f"Error loading SpaCy model: {e}")
    st.stop()

# --- Load Intents (data.json) ---
try:
    with open("data.json", "r", encoding="utf-8") as file:
        data = json.load(file)
except Exception as e:
    st.error(f"Could not load data.json: {e}")
    st.stop()

# --- NLP Based Response ---
def get_response_with_nlp(user_input):
    doc = nlp(user_input.lower())

    # Dengue check
    if any(token.text in ["dengue", "dengue fever"] for token in doc):
        for intent in data['intents']:
            if intent['tag'] == 'dengue_symptoms':
                return random.choice(intent['responses'])

    # Malaria check
    elif any(token.text in ["malaria"] for token in doc):
        for intent in data['intents']:
            if intent['tag'] == 'malaria_prevention':
                return random.choice(intent['responses'])

    # Hair fall example
    for intent in data['intents']:
        if intent['tag'] == 'hair_fall' and any(word in user_input for word in intent['patterns']):
            return random.choice(intent['responses'])

    # Greetings / Goodbye
    for intent in data['intents']:
        if intent['tag'] == 'greeting' and any(word in user_input for word in intent['patterns']):
            return random.choice(intent['responses'])
        if intent['tag'] == 'goodbye' and any(word in user_input for word in intent['patterns']):
            return random.choice(intent['responses'])

    # General health words
    if any(token.text in ["symptoms", "prevent", "prevention", "vaccination", "aware", "awareness", "helpline", "doctor", "health"] for token in doc):
        return "I can provide general information on common diseases like Dengue and Malaria. Please ask a specific question."

    # Default fallback
    return "I’m sorry, I’m not trained to answer that. Please contact a healthcare professional for accurate advice."

# --- Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input ---
if prompt := st.chat_input("Ask a health-related question..."):
    # Store user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    response = get_response_with_nlp(prompt)

    # Store bot message
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
