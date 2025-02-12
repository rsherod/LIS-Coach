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

# Display image
# This code attempts to open and display an image file named 'Low-Intensity Strategy AI Coach.png'.
# If successful, it shows the image with a caption. If there's an error, it displays an error message instead.
# You can customize this by changing the image file name and path. Supported image types include .png, .jpg, .jpeg, and .gif.
# To use a different image, replace 'Low-Intensity Strategy AI Coach.png' with your desired image file name (e.g., 'my_custom_image.jpg').
# Display image
image_path = 'Low-Intensity Strategy AI Coach.png'
try:
    image = Image.open(image_path)
    col1, col2, col3 = st.columns([1,6,1])
    with col2:
        st.image(image, use_container_width=True)
        st.markdown("<div style='text-align: center;'><small style='color: rgb(128, 128, 128);'>Created by Rebecca Sherod (2024)</small></div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center;'><small style='color: rgb(128, 128, 128);'>This work was supported, in part, by ASU's Mary Lou Fulton Teachers College (MLFTC). The opinions and findings expressed in this document are those of the author and do not necessarily reflect those of the funding agency.</small></div>", unsafe_allow_html=True)
except Exception as e:
    st.error(f"Error loading image: {e}")

# Title and BotDescription 
# You can customize the title, description, and caption by modifying the text within the quotes.
st.title("Welcome to the Virtual Low-Intensity Strategies Coach Platform!")
st.write("The goal of this bot is to assist you in selecting a low-intensity strategy that is a good fit for the interfering or challenging behavior you might be experiencing in your class school.\n\n**Directions:** Begin by providing some information about the behavior you are currently experiencing.")
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
    st.title("Settings")
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

# Debug information
# You can remove this by adding # in front of each line

st.sidebar.title("Debug Info")
for debug_msg in st.session_state.debug:
    st.sidebar.text(debug_msg)
