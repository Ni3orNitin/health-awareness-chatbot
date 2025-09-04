import streamlit as st
import json
import random

# Load the data from your JSON file
with open('data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

def get_response(user_input):
    """
    Finds the best response based on user input.
    A simple keyword-matching approach.
    """
    user_input = user_input.lower()
    
    # Check for keywords in each intent's patterns
    for intent in data['intents']:
        for pattern in intent['patterns']:
            # A simple check: if any word in the pattern is in the user's input
            if any(word in user_input for word in pattern.split()):
                return random.choice(intent['responses'])
                
    # Fallback response if no match is found
    return "I am sorry, I am not trained to answer that question. Please try rephrasing or ask about a different topic. For medical emergencies, please contact a healthcare professional."

# --- Streamlit UI Code ---

st.set_page_config(page_title="Odisha Health Awareness Chatbot")

# App title and description
st.title("👨‍⚕️ Odisha Health Awareness Chatbot")
st.markdown("Hi! I'm your virtual health assistant. Ask me anything about disease symptoms, prevention, or vaccination schedules.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask a health-related question..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get the chatbot's response
    response = get_response(prompt)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)