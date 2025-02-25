# Low-Intensity Strategies Coach (R. Sherod, fall 2024)
import streamlit as st
import google.generativeai as genai
from PIL import Image

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

# Custom CSS for the buttons
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

# Sidebar for strategies and settings
with st.sidebar:
    # Strategy section title first
    st.markdown("<h1 style='text-align: center;'>Low-Intensity Strategies</h1>", unsafe_allow_html=True)
    
    # Strategy buttons
    strategies = [
        "Active Supervision",
        "Behavior-Specific Praise",
        "High-Probability Request Sequences",
        "Instructional Choice",
        "Instructional Feedback",
        "Opportunities to Respond",
        "Precorrection"
    ]

    for strategy in strategies:
        if st.button(strategy):
            # Placeholder for future functionality
            pass
    
    # Add divider between strategies and settings
    st.divider()
    
    # Settings section
    st.markdown("<h1 style='text-align: center;'>Settings</h1>", unsafe_allow_html=True)
    st.caption("Note: Gemini-1.5-pro-002 can only handle 2 requests per minute, gemini-1.5-flash-002 can handle 15 per minute")

    # Ensure model_name is initialized
    if 'model_name' not in st.session_state:
        st.session_state.model_name = "gemini-2.0-pro-exp-02-05"  # default model

    model_option = st.selectbox(
        "Select Model:", ["gemini-2.0-pro-exp-02-05", "gemini-2.0-flash"]
    )

    # Update model_name if it has changed
    if model_option != st.session_state.model_name:
        st.session_state.model_name = model_option
        st.session_state.messages = []
        st.session_state.chat_session = None
    
    # Debug section at the bottom of sidebar
    st.divider()
    st.markdown("<h1 style='text-align: center;'>Debug Info</h1>", unsafe_allow_html=True)
    for debug_msg in st.session_state.debug:
        st.text(debug_msg)

# Load system prompt
def load_text_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        st.error(f"Error loading text file: {e}")
        return ""

system_prompt = load_text_file('instructions.txt')

# Create a main container for all content
main_container = st.container()

# Create a container for the funding acknowledgment that will appear at the bottom
funding_container = st.container()

# Now fill the main container with content
with main_container:
    # Display image
    image_path = 'LIS Image.jpg'
    try:
        image = Image.open(image_path)
        col1, col2, col3 = st.columns([1,10,1])
        with col2:
            st.image(image, use_container_width=True)
            st.markdown("<div style='text-align: center;'><small style='color: rgb(128, 128, 128);'>Bot created by Rebecca Sherod (2024)</small></div>", unsafe_allow_html=True)
          
    except Exception as e:
        st.error(f"Error loading image: {e}")

    # Title and BotDescription 
    st.markdown("<h2>Welcome to the Low-Intensity Strategies Bot!</h2>", unsafe_allow_html=True)
    st.write("The goal of this bot is to assist you in selecting a low-intensity strategy that fits your needs—whether you are proactively planning for engagement in your lessons or responding to an interfering or challenging behavior you are experiencing.\n\n**Directions:** If you would like to explore multiple low-intensity strategy options, type a description of the scenario you are experiencing or a lesson plan idea into the chat to get started. If you would like to focus on one strategy specifically, click the name of the strategy on the side menu to get started.")
    st.caption("Note: This Bot is under development and can make mistakes. Visit ci3t.org for information and resources about low-intensity strategies.")
    
    # Add extra spacing between caption and chat input
    st.write("")
    st.write("")
    st.write("")

    # Initialize Gemini client
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle form submission and generate response
    if st.session_state.should_generate_response:
        # Create combined prompt from responses
        combined_prompt = "Form Responses:\n"
        for q, a in st.session_state.form_responses.items():
            combined_prompt += f"{q}: {a}\n"
        
        # Add user message to chat history
        current_message = {"role": "user", "content": combined_prompt}
        st.session_state.messages.append(current_message)

        with st.chat_message("user"):
            st.markdown(current_message["content"])

        # Generate and display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            # Initialize chat session if needed
            if st.session_state.chat_session is None:
                generation_config = {
                    "temperature": st.session_state.temperature,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                }
                model = genai.GenerativeModel(
                    model_name=st.session_state.model_name,
                    generation_config=generation_config,
                )
                
                initial_messages = [
                    {"role": "user", "parts": [f"System: {system_prompt}"]},
                    {"role": "model", "parts": ["Understood. I will follow these instructions."]},
                ]
                
                if st.session_state.pdf_content:
                    initial_messages.extend([
                        {"role": "user", "parts": [f"The following is the content of an uploaded PDF document. Please consider this information when responding to user queries:\n\n{st.session_state.pdf_content}"]},
                        {"role": "model", "parts": ["I have received and will consider the PDF content in our conversation."]}
                    ])
                
                st.session_state.chat_session = model.start_chat(history=initial_messages)

            # Generate response with error handling
            try:
                response = st.session_state.chat_session.send_message(current_message["content"])
                full_response = response.text
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.session_state.debug.append("Assistant response generated")
            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}")
                st.session_state.debug.append(f"Error: {e}")

        st.session_state.should_generate_response = False
        st.rerun()

    # User input
    user_input = st.chat_input("Type here:")

    if user_input:
        # Add user message to chat history
        current_message = {"role": "user", "content": user_input}
        st.session_state.messages.append(current_message)

        with st.chat_message("user"):
            st.markdown(current_message["content"])

        # Generate and display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            # Prepare messages for Gemini API
            if st.session_state.chat_session is None:
                generation_config = {
                    "temperature": st.session_state.temperature,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                }
                model = genai.GenerativeModel(
                    model_name=st.session_state.model_name,
                    generation_config=generation_config,
                )
                
                # Initialize chat with system prompt and PDF content
                initial_messages = [
                    {"role": "user", "parts": [f"System: {system_prompt}"]},
                    {"role": "model", "parts": ["Understood. I will follow these instructions."]},
                ]
                
                if st.session_state.pdf_content:
                    initial_messages.extend([
                        {"role": "user", "parts": [f"The following is the content of an uploaded PDF document. Please consider this information when responding to user queries:\n\n{st.session_state.pdf_content}"]},
                        {"role": "model", "parts": ["I have received and will consider the PDF content in our conversation."]}
                    ])
                
                st.session_state.chat_session = model.start_chat(history=initial_messages)

            # Generate response with error handling
            try:
                if st.session_state.uploaded_file:
                    # If there's an uploaded file, include it in the generation
                    response = st.session_state.chat_session.send_message([
                        st.session_state.uploaded_file,
                        current_message["content"]
                    ])
                else:
                    # Otherwise, just use the text prompt
                    response = st.session_state.chat_session.send_message(current_message["content"])

                full_response = response.text
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.session_state.debug.append("Assistant response generated")

            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}")
                st.session_state.debug.append(f"Error: {e}")

        st.rerun()

# Now put the funding acknowledgment in the funding container (will appear at the bottom)
with funding_container:
    st.markdown("<div style='text-align: center; margin-top: 20px;'><small style='color: rgb(128, 128, 128);'>This bot is programmed with information from ci3t.org.\n\nThis work was supported, in part, by ASU's Mary Lou Fulton Teachers College (MLFTC). The opinions and findings expressed in this document are those of the author and do not necessarily reflect those of the funding agency.</small></div>", unsafe_allow_html=True)
