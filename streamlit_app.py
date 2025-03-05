# Low-Intensity Strategies Coach (R. Sherod, fall 2024)
import streamlit as st
import google.generativeai as genai
from PIL import Image

# Streamlit configuration
st.set_page_config(page_title="Streamlit Chatbot", layout="wide")

# Add this code between st.set_page_config(page_title="Streamlit Chatbot", layout="wide") and Display image code block
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
if "form_responses" not in st.session_state:
    st.session_state.form_responses = {}
if "should_generate_response" not in st.session_state:
    st.session_state.should_generate_response = False
# Add a new session state variable to track the active strategy
if "active_strategy" not in st.session_state:
    st.session_state.active_strategy = None

# Define strategy definitions dictionary
strategy_definitions = {
    "Behavior-Specific Praise": "Behavior-specific praise is classified as a form of positive reinforcement. It involves providing specific acknowledgement to let children and youth know they are meeting expectations in the classroom, at home, and in social settings. This can be given verbally, in writing, or through digital communication.",
    
    "Instructional Choice": "Instructional choice is the embedding of options into lessons for students to select based on their own preferences. It involves offering students two or more options, allowing them to independently select their preferred option, and providing each student with their selected option.",
    
    "Active Supervision": "Active supervision is when the adult, after giving a direction or cue with behavior expectations for a specific context, moves around the setting to scan, monitor, and respond effectively to behaviors. It involves reinforcing desired behaviors and correcting undesired behaviors.",
    
    "High-Probability Request Sequences": "High-probability request sequences involve making brief requests that students are very likely to comply with (at least 80% of the time) before making low-probability requests (those with 50% or less compliance). This strategy helps increase the likelihood of compliance with more challenging requests.",
    
    "Instructional Feedback": "Instructional feedback is a strategy for providing precise information to students about their academic, social, and behavioral performance. It helps clarify misunderstandings, confirm concepts, fine-tune understandings, and restructure current schemas, leading to increased intrinsic motivation.",
    
    "Opportunities to Respond": "Opportunities to respond is a strategy that helps students review material, acquire skill fluency, commit information to memory, increase on-task behavior, and reduce challenging behavior. It involves offering students frequent opportunities to respond to teacher questions or prompts about targeted academic materials.",
    
    "Precorrection": "Precorrection involves noting the behavior you would like to see before any challenging or undesirable behavior takes place. It helps address behavior problems proactively by anticipating problem behavior, reminding students of expected behaviors before transitions or activities, and reinforcing students for meeting expectations."
}

# Title and BotDescription 
# Check if a strategy is active and display its name and definition
if st.session_state.active_strategy:
    st.title(f"{st.session_state.active_strategy}")
    st.write(strategy_definitions.get(st.session_state.active_strategy, ""))
    st.write("**Directions:** Begin by providing some information about the behavior you are currently experiencing.")
else:
    # Default title and description when no strategy is selected
    st.title("Welcome to the Low-Intensity Strategies Bot!")
    st.write("The goal of this bot is to assist you in selecting a low-intensity strategy that is a good fit for the interfering or challenging behavior you might be experiencing in your classroom.\n\n**Directions:** Begin by providing some information about the behavior you are currently experiencing.")

st.caption("Note: This Bot can make mistakes.")

# Initialize Gemini client
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Initialize session state
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
if "uploaded_file" not in st.session_state:  # Add this line
    st.session_state.uploaded_file = None

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
    
    #if uploaded_pdf:
        #try:
            # Upload file using File API with mime_type specified
            #uploaded_file = genai.upload_file(uploaded_pdf, mime_type="application/pdf")
            #st.session_state.uploaded_file = uploaded_file
            #st.success("File uploaded successfully!")
        #except Exception as e:
            #st.error(f"Error uploading file: {e}")
            #st.session_state.debug.append(f"File upload error: {e}")
    
    
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
        if st.button(strategy):
            # Update active strategy when a button is clicked
            st.session_state.active_strategy = strategy
            st.rerun()  # Rerun to update the UI

    # Debug section
    st.markdown("<h1 style='text-align: center;'>Debug Info</h1>", unsafe_allow_html=True)
    for debug_msg in st.session_state.debug:
        st.sidebar.text(debug_msg)

# Load system prompt
def load_text_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        st.error(f"Error loading text file: {e}")
        return ""

system_prompt = load_text_file('instructions.txt')

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
# The placeholder text "Your message:" can be customized to any desired prompt, e.g., "Message Creative Assistant...".
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

# Add footnote at the bottom of the page
st.markdown("<div style='text-align: center; margin-top: 20px;'><small style='color: rgb(128, 128, 128);'>Created by Rebecca Sherod (2024)</small></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center;'><small style='color: rgb(128, 128, 128);'>This work was supported, in part, by ASU's Mary Lou Fulton Teachers College (MLFTC). The opinions and findings expressed in this document are those of the author and do not necessarily reflect those of the funding agency.</small></div>", unsafe_allow_html=True)
