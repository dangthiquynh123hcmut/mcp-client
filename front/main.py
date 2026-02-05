import streamlit as st
import asyncio
import httpx
from api_client import APIClient

st.set_page_config(page_title="MCP Chatbot", layout="wide")

# Initialize session state
if "api_client" not in st.session_state:
    st.session_state.api_client = APIClient()

if "tools" not in st.session_state:
    st.session_state.tools = []

async def load_tools():
    """Load available tools"""
    try:
        tools = await st.session_state.api_client.get_tools()
        st.session_state.tools = tools
    except Exception as e:
        st.error(f"Failed to load tools: {str(e)}")

async def send_query(query: str):
    """Send query to backend"""
    try:
        messages = await st.session_state.api_client.query(query)
        return messages
    except Exception as e:
        st.error(f"Query failed: {str(e)}")
        return None

# UI
st.title("🤖 MCP Chatbot")

# Load tools on startup
with st.spinner("Loading tools..."):
    asyncio.run(load_tools())

# Display available tools
st.sidebar.header("Available Tools")
if st.session_state.tools:
    for tool in st.session_state.tools:
        st.sidebar.write(f"**{tool['name']}**")
        st.sidebar.caption(tool['description'])
else:
    st.sidebar.info("No tools available")

# Query input
query = st.text_input("Enter your query:", placeholder="Ask me anything...")

if query:
    with st.spinner("Processing..."):
        messages = asyncio.run(send_query(query))
    
    if messages:
        st.subheader("Response")
        for msg in messages:
            if msg['role'] == 'assistant':
                st.write(f"**Assistant:** {msg['content']}")
            else:
                st.write(f"**User:** {msg['content']}")