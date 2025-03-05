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
st.markdown("""
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
""", unsafe_allow_html=True)

# Helper function to load text files
def load_text_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        st.error(f"Error loading text file: {e}")
        return ""

# Helper function to load JSON files
def load_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        st.error(f"Error loading JSON file: {e}")
        return {}

# Load system instructions and strategy data
system_instructions = load_text_file('instructions.txt')
strategies_data = {}

# Define the paths to both JSON files
strategies_json_path = 'Strategies.json'

# Load the first JSON file if it exists
if os.path.exists(strategies_json_path):
    strategies_data.update(load_json_file(strategies_json_path))
    st.session_state.debug.append(f"Loaded strategies from {strategies_json_path}")
else:
    st.session_state.debug.append(f"Warning: {strategies_json_path} not found")


# Function to build the complete system prompt
def build_system_prompt(active_strategy=None):
    # Start with base instructions
    prompt = system_instructions
    
    # Add strategy information
    if strategies_data:
        prompt += "\n\n## Strategy Information\n\n"
        
        # If a specific strategy is selected, only include that one
        if active_strategy and active_strategy in strategies_data:
            prompt += f"Selected Strategy: {active_strategy}\n\n"
            prompt += json.dumps({active_strategy: strategies_data[active_strategy]}, indent=2)
            prompt += "\n\nIMPORTANT: You must ONLY discuss and recommend the selected strategy above. Do not mention or suggest other strategies even if they might be relevant. If asked about other strategies, politely redirect the conversation to focus on the selected strategy or suggest clicking a different strategy button in the sidebar."
        else:
            # Otherwise include all strategies
            prompt += json.dumps(strategies_data, indent=2)
    
    return prompt

# Sidebar for model and temperature selection
with st.sidebar:
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

   
    # File upload for PDF
    #st.title("Upload Intervention Grid Here:")
    #uploaded_pdf = st.file_uploader("Upload:", type=["pdf"])
    
    
    
    # Clear chat functionality
    #clear_button = st.button("Clear Chat")
    #if clear_button:
        #st.session_state.messages = []
        #st.session_state.debug = []
        #st.session_state.pdf_content = ""
        #st.session_state.chat_session = None
        #st.success("Chat cleared!")
        #st.experimental_rerun()  # use rerun to refresh the app

    # Add divider before strategy buttons
    st.divider()
    
    # Strategy section title
    st.markdown("<h1 style='text-align: center;'>Low-Intensity Strategies</h1>", unsafe_allow_html=True)
    
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

    # Strategy buttons
    strategies = [
        "Behavior-Specific Praise",
        "Instructional Choice",
        "Active Supervision",
        "High-Probability Request Sequences",
        "Instructional Feedback",
        "Opportunities to Respond",
        "Precorrection"
    ]

    for strategy in strategies:
        # Use a unique key for each button to avoid conflicts during re-renders
        button_key = f"strategy_button_{strategy}"
        
        # Determine if the current strategy is active
        is_active = st.session_state.active_strategy == strategy
        
        # Use different styling based on whether the button is active
        button_class = "active-strategy" if is_active else "strategy-button"
        
        # Button logic: if the button is clicked, set the session state appropriately
        if st.button(strategy, key=button_key, disabled=is_active, help="Click to explore this strategy"):
            st.session_state.active_strategy = strategy  # Activate the strategy
            st.session_state.messages = []  # Clear chat history when switching strategies
            st.session_state.chat_session = None #reset session
            st.rerun()

        if is_active:
            if st.button(f"Return to All Strategies", key=f"return_button_{strategy}"):  # A second button to deactivate
                st.session_state.active_strategy = None # Clear the active strategy
                st.session_state.messages = []  # Clear chat history when switching strategies
                st.session_state.chat_session = None #reset session
                st.rerun()

    # Debug section
    st.markdown("<h1 style='text-align: center;'>Debug Info</h1>", unsafe_allow_html=True)
    for debug_msg in st.session_state.debug:
        st.sidebar.text(debug_msg)
# Create a main container for all content
main_container = st.container()

# Create a container for the funding acknowledgment that will appear at the bottom
funding_container = st.container()

# Now fill the main container with content
with main_container:
    # Title and BotDescription with dynamic header based on active strategy
    if st.session_state.active_strategy:
        st.markdown(f"<h2>Focus on {st.session_state.active_strategy}</h2>", unsafe_allow_html=True)
        
        # First message intro for active strategy
        if not st.session_state.messages:
            strategy_intros = {
                "Active Supervision": "Active Supervision involves moving, scanning, and interacting with students to prevent and address behavior concerns.",
                "Behavior-Specific Praise": "Behavior-Specific Praise is a form of positive reinforcement that acknowledges specific student behaviors.",
                "High-Probability Request Sequences": "High-Probability Request Sequences involve making requests students are likely to comply with before making more challenging requests.",
                "Instructional Choice": "Instructional Choice involves embedding options into lessons for students to select based on their preferences.",
                "Instructional Feedback": "Instructional Feedback provides precise information to students about their academic, social, and behavioral performance.",
                "Opportunities to Respond": "Opportunities to Respond involves offering frequent opportunities for students to engage with academic material.",
                "Precorrection": "Precorrection involves proactively reminding students of expected behaviors before challenging situations arise."
            }
            
            intro = strategy_intros.get(st.session_state.active_strategy, "")
            st.write(f"You're currently exploring the {st.session_state.active_strategy} strategy. {intro}")
            st.write("Ask questions about how to implement this strategy in your classroom or describe a scenario where you might use it.")
        else:
            st.write(f"You're currently exploring the {st.session_state.active_strategy} strategy. Ask questions about how to implement this strategy in your classroom or how it can help with specific scenarios.")
    else:
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
                
                # Build complete system prompt with active strategy if applicable
                complete_system_prompt = build_system_prompt(st.session_state.active_strategy)
                
                initial_messages = [
                    {"role": "user", "parts": [f"System: {complete_system_prompt}"]},
                    {"role": "model", "parts": ["Understood. I will follow these instructions."]},
                ]
                
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

    # User input with context-aware placeholder
    placeholder_text = "Ask about how to use this strategy in your classroom" if st.session_state.active_strategy else "Describe a classroom scenario or ask about low-intensity strategies"
    user_input = st.chat_input(placeholder_text)

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
                
                # Build complete system prompt with active strategy if applicable
                complete_system_prompt = build_system_prompt(st.session_state.active_strategy)
                
                # Initialize chat with system prompt
                initial_messages = [
                    {"role": "user", "parts": [f"System: {complete_system_prompt}"]},
                    {"role": "model", "parts": ["Understood. I will follow these instructions."]},
                ]
                
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

        st.rerun()

# Now put the funding acknowledgment in the funding container (will appear at the bottom)
with funding_container:
    st.markdown("<div style='text-align: center; margin-top: 20px;'><small style='color: rgb(128, 128, 128);'>This bot is programmed with information from ci3t.org.\n\nThis work was supported, in part, by ASU's Mary Lou Fulton Teachers College (MLFTC). The opinions and findings expressed in this document are those of the author and do not necessarily reflect those of the funding agency.</small></div>", unsafe_allow_html=True)
