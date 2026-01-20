import streamlit as st
import requests

# --- CONFIGURATION ---
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Corporate Chatbot (RBAC)", layout="wide")

# --- SESSION STATE INITIALIZATION ---
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR: LOGIN SYSTEM ---
with st.sidebar:
    st.header("🔐 Secure Login")
    
    if not st.session_state.token:
        # Login Form
        username = st.text_input("Username", placeholder="e.g., finance_user")
        password = st.text_input("Password", type="password", placeholder="e.g., finance123")
        
        if st.button("Login"):
            try:
                response = requests.post(
                    f"{API_URL}/token",
                    data={"username": username, "password": password}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.token = data["access_token"]
                    st.session_state.role = data["role"]
                    st.success(f"Welcome! Role: {data['role']}")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            except Exception as e:
                st.error(f"Connection Error: {e}")
    else:
        # Logout Button
        st.success(f"👤 Logged in as: **{st.session_state.role}**")
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.role = None
            st.session_state.messages = []
            st.rerun()

# --- MAIN CHAT INTERFACE ---
st.title("🤖 Internal Corporate Assistant")
st.markdown("ask questions about **Finance, HR, or Engineering** based on your role.")

if st.session_state.token:
    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ask a question..."):
        # 1. Display User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Call Backend API
        with st.chat_message("assistant"):
            with st.spinner("Thinking (and checking permissions)..."):
                try:
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    response = requests.post(
                        f"{API_URL}/chat",
                        json={"question": prompt},
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        answer = result["answer"]
                        sources = result["sources"]
                        
                        # Display Answer
                        st.markdown(answer)
                        
                        # Display Sources (Professional Touch)
                        if sources:
                            st.info(f"📚 Sources: {', '.join(sources)}")
                        
                        # Save to history
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    else:
                        error_msg = "Error: " + response.json().get("detail", "Unknown error")
                        st.error(error_msg)
                except Exception as e:
                    st.error(f"Failed to connect to backend: {e}")

else:
    # Welcome Screen for Logged Out Users
    st.info("👋 Please log in using the sidebar to access corporate data.")
    st.markdown("""
    **Demo Credentials:**
    - **Finance:** `finance_user` / `finance123`
    - **HR:** `hr_user` / `hr123`
    - **Engineering:** `eng_user` / `eng123`
    """)