# Low-Intensity Strategies Coach (R. Sherod, fall 2024)
import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import os

# Streamlit configuration
st.set_page_config(page_title="Streamlit Chatbot", layout="wide")

# Initialize session state variables
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
if "form_responses" not in st.session_state:
    st.session_state.form_responses = {}
if "should_generate_response" not in st.session_state:
    st.session_state.should_generate_response = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model_name" not in st.session_state:
    st.session_state.model_name = "gemini-2.0-pro-exp-02-05"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.5
if "debug" not in st.session_state:
    st.session_state.debug = []
if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "active_strategy" not in st.session_state:
    st.session_state.active_strategy = None

# IMPORTANT: Apply custom CSS styles immediately after page config to ensure they work
st.markdown(
    """
<style>
    /* Style for strategy buttons - purple style */
    .strategy-button > button {
        background-color: #6A157D !important;
        color: white !important;
        border-radius: 20px !important;
        padding: 10px 15px !important;
        border: none !important;
        width: 100% !important;
        margin: 5px 0 !important;
    }
    .strategy-button > button:hover {
        background-color: #871BA1 !important;
        color: white !important;
    }

    /* Style for Clear Chat button - default style */
    .clear-chat-button > button {
        background-color: transparent !important;
        color: rgb(38, 39, 48) !important;
        border: 1px solid rgba(49, 51, 63, 0.2) !important;
        border-radius: 4px !important;
        padding: 0.25rem 0.75rem !important;
        width: 100% !important;
        margin: 5px 0 !important;
    }
    .clear-chat-button > button:hover {
        border-color: rgb(49, 51, 63) !important;
        color: rgb(49, 51, 63) !important;
    }

    /* Style for active strategy button - darker purple */
    .active-strategy > button {
        background-color: #4A0D59 !important;
        color: white !important;
        border-radius: 20px !important;
        padding: 10px 15px !important;
        border: none !important;
        width: 100% !important;
        margin: 5px 0 !important;
    }
    .active-strategy > button:hover {
        background-color: #871BA1 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Helper function to load text files
def load_text_file(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read()
    except Exception as e:
        st.error(f"Error loading text file: {e}")
        return ""

# Helper function to load JSON files
def load_json_file(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception as e:
        st.error(f"Error loading JSON file: {e}")
        return {}

# Load system instructions and strategy data
system_instructions = load_text_file("instructions.txt")
strategies_data = {}

# Define the paths to both JSON files
strategies_json_path1 = "AS_BSP_HP_IC_combined.json"
strategies_json_path2 = "IF_OTR_P_combined.json"

# Load the first JSON file if it exists
if os.path.exists(strategies_json_path1):
    strategies_data.update(load_json_file(strategies_json_path1))
    st.session_state.debug.append(f"Loaded strategies from {strategies_json_path1}")
else:
    st.session_state.debug.append(f"Warning: {strategies_json_path1} not found")

# Load the second JSON file if it exists
if os.path.exists(strategies_json_path2):
    strategies_data.update(load_json_file(strategies_json_path2))
    st.session_state.debug.append(f"Loaded strategies from {strategies_json_path2}")
else:
    st.session_state.debug.append(f"Warning: {strategies_json_path2} not found")

# Function to build the complete system prompt
def build_system_prompt(active_strategy=None):
    prompt = system_instructions
    if strategies_data:
        prompt += "\n\n## Strategy Information\n\n"
        if active_strategy and active_strategy in strategies_data:
            prompt += f"Selected Strategy: {active_strategy}\n\n"
            prompt += json.dumps({active_strategy: strategies_data[active_strategy]}, indent=2)
            prompt += "\n\nIMPORTANT: You must ONLY discuss and recommend the selected strategy above. Do not mention or suggest other strategies even if they might be relevant. If asked about other strategies, politely redirect the conversation to focus on the selected strategy or suggest clicking a different strategy button in the sidebar."
        else:
            prompt += json.dumps(strategies_data, indent=2)
    return prompt

# Sidebar for model and temperature selection
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>Settings</h1>", unsafe_allow_html=True)
    st.caption("Note: Gemini-1.5-pro-002 can only handle 2 requests per minute, gemini-1.5-flash-002 can handle 15 per minute")
    if "model_name" not in st.session_state:
        st.session_state.model_name = "gemini-2.0-pro-exp-02-05"
    model_option = st.selectbox("Select Model:", ["gemini-2.0-pro-exp-02-05", "gemini-2.0-flash"])
    if model_option != st.session_state.model_name:
        st.session_state.model_name = model_option
        st.session_state.messages = []
        st.session_state.chat_session = None
    st.divider()
    st.markdown("<h1 style='text-align: center;'>Low-Intensity Strategies</h1>", unsafe_allow_html=True)
    button_style = """
        <style>
            .stButton > button {
                background-color: #6A157D;
                color: white;
                border-radius: 20px;
                padding: 10px 15px;
                border: none;
                width: 100%;
                margin: 5px 0;
            }
            .stButton > button:hover {
                background-color: #871BA1;
                color: white !important;
            }
        </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)
strategies = [
    "Behavior-Specific Praise",
    "Instructional Choice",  # <-- Likely fixed this line
    "Active Supervision",
    "High-Probability Request Sequences",
    "Instructional Feedback", # <-- Or this line
    "Opportunities to Respond",
    "Precorrection",
]
