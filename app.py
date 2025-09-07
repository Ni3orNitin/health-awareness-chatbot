import streamlit as st
import json
import random
import spacy
import subprocess
import sys
from rapidfuzz import fuzz



import streamlit as st
import subprocess
import sys

# Try to install blis if it's not present
try:
    import blis
except ImportError:
    st.info("Installing blis...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "blis==0.7.11"]) # Or whatever version you need
    st.experimental_rerun()

# --- Spacy Model Setup ---
# This function ensures the model is downloaded for deployment.
@st.cache_resource
def load_spacy_model():
    model_name = "en_core_web_sm"
    try:
        nlp = spacy.load(model_name)
    except OSError:
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
st.title("🩺 Odisha Health Awareness Chatbot")

# Load the data from your JSON file
with open('data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# --- Chatbot response logic ---
def get_response(user_input):
    user_input_lower = user_input.lower().strip()
    
    # 1. Exact Pattern Match (High Confidence)
    for intent in data['intents']:
        if user_input_lower in [p.lower() for p in intent['patterns']]:
            return random.choice(intent['responses'])
    
    # 2. Keyword-Based Matching (More Flexible with Fuzzy Matching)
    keywords = ["malaria", "dengue", "covid"] # You can expand this list
    
    # Use fuzzy matching to find the best keyword match
    found_keyword = None
    best_score = 0
    fuzzy_match_threshold = 80 # A score of 80 or higher is considered a match
    
    for keyword in keywords:
        score = fuzz.partial_ratio(user_input_lower, keyword)
        if score > best_score and score >= fuzzy_match_threshold:
            best_score = score
            found_keyword = keyword
            
    if found_keyword:
        # Check if the user is asking for a specific type of information (symptoms/precautions)
        if "symptoms" in user_input_lower:
            for intent in data['intents']:
                if intent['tag'].lower() == f"{found_keyword}_symptoms":
                    return random.choice(intent['responses'])
        elif "precautions" in user_input_lower or "prevent" in user_input_lower:
            for intent in data['intents']:
                if intent['tag'].lower() == f"{found_keyword}_precautions":
                    return random.choice(intent['responses'])
        else:
            # If only the disease name is provided, return a general response
            for intent in data['intents']:
                if found_keyword in intent['tag'].lower():
                    return random.choice(intent['responses'])
    
    # 3. Final Fallback if no match is found
    return "❌ Sorry, I don't have information about that. Please ask about Malaria, Dengue, or other common health topics."

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []



# --- Sidebar Quick Buttons ---
st.sidebar.title("⚡ Quick Questions")
if st.sidebar.button("🦟 Malaria Symptoms"):
    st.session_state.messages.append({"role": "user", "text": "What are malaria symptoms?"})
    response = get_response("What are malaria symptoms?")
    st.session_state.messages.append({"role": "assistant", "text": response})

if st.sidebar.button("🩸 Dengue Symptoms"):
    st.session_state.messages.append({"role": "user", "text": "What are dengue symptoms?"})
    response = get_response("What are dengue symptoms?")
    st.session_state.messages.append({"role": "assistant", "text": response})

if st.sidebar.button("🦠 Covid Precautions"):
    st.session_state.messages.append({"role": "user", "text": "What are covid precautions?"})
    response = get_response("What are covid precautions?")
    st.session_state.messages.append({"role": "assistant", "text": response})

if st.sidebar.button("🩺 General Health Tips")  :
    st.session_state.messages.append({"role": "user", "text": "What are some general health tips?"})
    response = get_response("What are some general health tips?")
    st.session_state.messages.append({"role": "assistant", "text": response})

if st.sidebar.button("📞 Emergency Numbers"):
    st.session_state.messages.append({"role": "user", "text": "Emergency Numbers"})
    response = get_response("Emergency Numbers")
    st.session_state.messages.append({"role": "assistant", "text": response})

if st.sidebar.button("💊 Nearby Hospitals"):
    st.session_state.messages.append({"role": "user", "text": "Nearby Hospitals"})
    response = get_response("Nearby Hospitals")
    st.session_state.messages.append({"role": "assistant", "text": response})

if st.sidebar.button("🌡️ Fever Management") :
    st.session_state.messages.append({"role": "user", "text": "Fever Management"})
    response = get_response("Fever Management")
    st.session_state.messages.append({"role": "assistant", "text": response})

if st.sidebar.button("🤒 Cold & Cough Remedies"):
    st.session_state.messages.append({"role": "user", "text": "Cold and Cough Remedies"})
    response = get_response("Cold and Cough Remedies")
    st.session_state.messages.append({"role": "assistant", "text": response})

if st.sidebar.button("❓ Help"):
    st.session_state.messages.append({"role": "user", "text": "Help"})
    response = get_response("Help")
    st.session_state.messages.append({"role": "assistant", "text": response})

if st.sidebar.button("ℹ️ About"):
    st.session_state.messages.append({"role": "user", "text": "About"})
    response = get_response("About")
    st.session_state.messages.append({"role": "assistant", "text": response})   



# --- Chat input box ---
user_input = st.chat_input("Ask me about health topics...")
if user_input:
    st.session_state.messages.append({"role": "user", "text": user_input})
    response = get_response(user_input)
    st.session_state.messages.append({"role": "assistant", "text": response})

# --- Chat history display ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["text"])