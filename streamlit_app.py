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
strategies_json_path1 = 'AS_BSP_HP_IC_combined.json'
strategies_json_path2 = 'IF_OTR_P_combined.json'

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

# Dictionary of strategy definitions
strategy_definitions = {
    "Behavior-Specific Praise": "Behavior-specific praise is classified as a form of positive reinforcement, using behavior analytic terms. When something desirable (e.g., attention, activity/tangible, sensory) is received after a behavior, it is more likely the behavior will increase in the future.",
    
    "Instructional Choice": "Instructional choice is the embedding of options into lessons for students to select based on their own preferences. It involves offering students two or more options, allowing them to independently select the option of most interest to them.",
    
    "Active Supervision": "Active supervision is when the adult, following giving a direction or cue with behavior expectations for a specific context, moves around the specific setting to scan, monitor and respond effectively to behaviors.",
    
    "High-Probability Request Sequences": "High-probability requests are brief requests that the student is very likely to comply with (at least 80% of the time). This strategy involves making high-probability requests before making low-probability requests.",
    
    "Instructional Feedback": "Instructional feedback is a low-intensity strategy for providing precise information to students about their academic, social, and behavioral performance.",
    
    "Opportunities to Respond": "Opportunities to respond is a low-intensity, teacher-delivered strategy that helps students review material, acquire skill fluency, commit information to memory, increase on-task behavior, and reduce challenging behavior.",
    
    "Precorrection": "Precorrection involves noting the behavior you would like to see, with the cue or prompt taking place before any challenging or undesirable behavior takes place. This strategy helps address behavior problems before they occur."
}

# Function to reset chat when switching strategies
def reset_chat():
    st.session_state.messages = []
    st.session_state.chat_session = None

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

    # Clear chat button
    if st.button("Clear Chat", key="clear_chat"):
        reset_chat()
        st.success("Chat cleared!")
        st.rerun()
   
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

    # Function to handle strategy selection
    def set_active_strategy(strategy):
        st.session_state.active_strategy = strategy
        reset_chat()  # Reset chat when switching strategies

    # Create buttons for each strategy
    for strategy in strategies:
        button_key = f"btn_{strategy.replace(' ', '_').lower()}"
        if st.button(strategy, key=button_key):
            set_active_strategy(strategy)
            st.rerun()  # Rerun to update the UI immediately

    # Debug section
    st.markdown("<h1 style='text-align: center;'>Debug Info</h1>", unsafe_allow_html=True)
    for debug_msg in st.session_state.debug:
        st.sidebar.text(debug_msg)

# Return to Home button if a strategy is active
if st.session_state.active_strategy:
    if st.button("← Return to Home"):
        st.session_state.active_strategy = None
        reset_chat()
        st.rerun()

# Create a main container for all content
main_container = st.container()

# Create a container for the funding acknowledgment that will appear at the bottom
funding_container = st.container()

# Now fill the main container with content
with main_container:
    # Display image (only on main page)
    image_path = 'LIS Image.jpg'
    try:
        image = Image.open(image_path)
        if not st.session_state.active_strategy:  # Only show on main page
            col1, col2, col3 = st.columns([1,6,1])
            with col2:
                st.image(image, use_container_width=True)
                st.markdown("<div style='text-align: center;'><small style='color: rgb(128, 128, 128);'>Created by Rebecca Sherod (2024)</small></div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align: center;'><small style='color: rgb(128, 128, 128);'>This work was supported, in part, by ASU's Mary Lou Fulton Teachers College (MLFTC). The opinions and findings expressed in this document are those of the author and do not necessarily reflect those of the funding agency.</small></div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading image: {e}")

    # Title and BotDescription with dynamic header based on active strategy
    if st.session_state.active_strategy:
        st.title(st.session_state.active_strategy)
        st.info(strategy_definitions.get(st.session_state.active_strategy, ""))
        st.write(f"Ask questions about how to implement {st.session_state.active_strategy} in your classroom or describe a scenario where you might use it.")
    else:
        st.title("Welcome to the Low-Intensity Strategies Bot!")
        st.write("The goal of this bot is to assist you in selecting a low-intensity strategy that is a good fit for the interfering or challenging behavior you might be experiencing in your classroom.\n\n**Directions:** Begin by providing some information about the behavior you are currently experiencing, or click on a strategy in the sidebar to learn more about it.")
    
    st.caption("Note: This Bot can make mistakes.")

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
    placeholder_text = "Ask about this strategy..." if st.session_state.active_strategy else "Type here:"
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
    if not st.session_state.active_strategy:  # Only show on main page
        st.markdown("<div style='text-align: center; margin-top: 20px;'><small style='color: rgb(128, 128, 128);'>This bot is programmed with information from ci3t.org.</small></div>", unsafe_allow_html=True)
