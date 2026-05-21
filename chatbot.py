# app.py
#import app
from dotenv import load_dotenv # Loads variables from .env file
import os # Used to access environment variables
import streamlit as st # Streamlit for web app UI
from groq_llm import GroqLLM # Import custom Groq LLM class

#  1) Load env & validate 
load_dotenv() # Loads .env file
if not os.getenv("GROQ_API_KEY"): # check if API key exists
    st.error("GROQ_API_KEY not found in .env") # Show error if key is missing
    st.stop() # Stop execution if key is missing

# 2) Page config 
st.set_page_config( # Set Streamlit page settings
    page_title="Ask Anything Chatbot", # Title of the page
    page_icon="💡", # Icon in tab
    layout="wide", # Makes UI wider(better UX)
)

#  3) Session state helpers 
def init_history(): # Function to initialize chat memory
    if "history" not in st.session_state: # Check if history exists
        st.session_state.history = [] # Create empty list to store conversation history

def clear_history(): # Function to clear chat history
    st.session_state.history = [] # Clears conversation

init_history() # Ensure history is always initialized

# 4) Sidebar controls 
with st.sidebar: # Everything inside this block goes to the sidebar
    st.header("Settings") # Header for sidebar
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.05) # Slider to control response randomness
    if st.button(" Clear Chat"): # Button to reset chat
        clear_history() # calls reset function
    if st.session_state.history: # If there is conversation history, show download option
        transcript = "\n\n".join(
            f"You: {u}\nBot: {b}" for u, b in st.session_state.history
        ) # Format conversation history as text
        st.download_button(
            " Download Transcript", # Button lable
            transcript, # File content to download
            file_name="chat_transcript.txt", # file name
            mime="text/plain", # file type
        ) # Button to download conversation history as a text file

#  5) Main chat UI 
st.title("Chatbot") # Main heading
st.markdown("Enter any question ") # Subtitle text

# Display prior messages
for user_msg, bot_msg in st.session_state.history: # Loop through conversation history
    st.chat_message("user").write(user_msg) # Display user message 
    st.chat_message("assistant").write(bot_msg) # Display bot response

# Capture new user input
if user_input := st.chat_input("Type your message here..."): # Input box for user to type message
    # := → assigns + checks at same time
    # Build context-aware prompt
    convo_context = "".join(
        f"User: {u}\nBot: {b}\n" for u, b in st.session_state.history
    ) # Create conversation context from history
    full_prompt = (
        "You are a helpful, knowledgeable assistant.\n" # Instruction for the bot
        f"{convo_context}" # Add conversation history to prompt for context
        f"User: {user_input}\n" # Adds new question
        "Bot:" # Signal that bot should respond next
    )

    llm = GroqLLM(temperature=temperature) # Initialize custom Groq LLM with selected temperature
    with st.spinner("Thinking…"): # Show loading spinner while waiting for response
        try:
            bot_response = llm(full_prompt) # Calls the custom Groq LLM
        except Exception as e:
            bot_response = f"Error: {e}"

    # Append and display
    st.session_state.history.append((user_input, bot_response)) # Save new conversation to history
    st.chat_message("user").write(user_input) # Display new user message 
    st.chat_message("assistant").write(bot_response) # Display new bot response
    
    

# Loads API key
# Builds UI with Streamlit
# Stores chat history
# Creates context-aware prompts
# Sends to Groq LLM
# Displays responses
# Allows download + reset
