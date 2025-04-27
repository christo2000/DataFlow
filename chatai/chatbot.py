import os
import streamlit as st
from groq import Groq
import streamlit.components.v1 as components
from db_connection import Resources
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection to retrieve API keys and model
db_url = os.getenv("DB_URL")
db_values = Resources(db_url)
values = db_values.resource_value_retrieval()

# Initialize Groq client
client = Groq(api_key=values.get("GROQ_API_KEY"))
model_name = values.get("MODEL_NAME")

# Streamlit app
st.set_page_config(page_title="ChatAI", layout="centered")
st.title("🤖 ChatAI with Groq")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar options
def clear_chat():
    st.session_state.messages.clear()

with st.sidebar:

    # Read the local HTML file
    with open("/media/christopher/New Volume/workspace/project/DataFlow/3d.html", "r") as file:
        html_content = file.read()
    html_with_size = f"""
    <div style="width: 200px; height: 200px; overflow: hidden;">
        {html_content}</div>
    """
    st.markdown(html_with_size, unsafe_allow_html=True)

    # System message input and chat settings
    st.header("Settings")

    # System prompt input area
    system_prompt = st.text_area("System Message", "You are a helpful assistant.")

    # Option to toggle chat history visibility
    show_history = st.checkbox("Show Chat History", value=True)

    # Button to clear chat history
    st.button("🗑️ Clear Chat", on_click=clear_chat)

# Display chat messages only if checkbox is checked
if show_history:
    with open("response_file/chat_history.txt", "a") as file:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
            file.write(str(msg))

# User input
user_input = st.chat_input("Ask me anything...")
if user_input:
    # Append user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response using Groq API
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            *st.session_state.messages,
        ],
        model=model_name,
    )

    ai_reply = response.choices[0].message.content

    # Append assistant message to chat history
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})

    with st.chat_message("assistant"):
        st.markdown(ai_reply)
