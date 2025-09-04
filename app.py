import streamlit as st
import json
import random
import spacy

# Load the spaCy NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    st.error("SpaCy model not found. Please run 'python -m spacy download en_core_web_sm' in your terminal.")
    st.stop()

# Load the data from your JSON file
with open('data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

def get_response_with_nlp(user_input):
    """
    Finds a response based on NLP entity recognition.
    """
    doc = nlp(user_input.lower())

    # Look for specific disease entities in the user's input
    if any(token.text in ["dengue", "dengue fever"] for token in doc):
        for intent in data['intents']:
            if intent['tag'] == 'dengue_symptoms':
                return random.choice(intent['responses'])

    elif any(token.text in ["malaria"] for token in doc):
        for intent in data['intents']:
            if intent['tag'] == 'malaria_prevention':
                return random.choice(intent['responses'])
    
    # You can add more specific rules here for other diseases or keywords
    
    # Simple fallback for greetings and goodbye
    for intent in data['intents']:
        if intent['tag'] == 'greeting' and any(token.text in intent['patterns'] for token in doc):
            return random.choice(intent['responses'])
        if intent['tag'] == 'goodbye' and any(token.text in intent['patterns'] for token in doc):
            return random.choice(intent['responses'])
    
    # Fallback for general health queries
    if any(token.text in ["symptoms", "prevent", "prevention", "vaccination", "aware", "awareness", "helpline", "doctor", "health"] for token in doc):
        return "I can provide general information on common diseases like Dengue and Malaria. Please ask a specific question."
    
    # Final fallback if nothing is recognized
    return "I am sorry, I am not trained to answer that question. For medical emergencies, please contact a healthcare professional. "

# --- Streamlit UI Code ---
st.set_page_config(page_title="Odisha Health Awareness Chatbot")
st.title("👨‍⚕️ Odisha Health Awareness Chatbot")
st.markdown("Hi! I'm your virtual health assistant. Ask me anything about disease symptoms, prevention, or vaccination schedules.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a health-related question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = get_response_with_nlp(prompt)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)