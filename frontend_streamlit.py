import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(page_title="Feedback Chatbot", layout="centered")
st.title("📝 Feedback Chatbot Dashboard")

API_URL = "http://127.0.0.1:8000"  # Adjust if backend runs elsewhere

# --- Chat with Feedback Bot ---
st.header("💬 Chat with Feedback Bot")
chat_input = st.text_input("Ask a question about the feedback:")
if st.button("Ask Bot") and chat_input:
    with st.spinner("Getting answer..."):
        try:
            resp = requests.post(f"{API_URL}/chat-with-crew/?question={chat_input}")

            if resp.ok:
                data = resp.json()
                st.success(data.get("answer", "No answer returned."))
                sources = data.get("sources", [])
                if sources:
                    st.markdown("*Sources:*")
                    for src in sources:
                        st.json(src)
            else:
                st.error(f"Error: {resp.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")

# --- Upload Feedback CSV ---
st.header("📤 Upload Feedback CSV")
uploaded_file = st.file_uploader("Upload a CSV file with 'respondent' and 'feedback' columns:", type=["csv"])
if st.button("Upload CSV") and uploaded_file:
    with st.spinner("Uploading and analyzing..."):
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
            resp = requests.post(f"{API_URL}/upload-csv/", files=files)
            if resp.ok:
                data = resp.json()
                st.success(data.get("message", "Upload successful."))
            else:
                st.error(f"Error: {resp.text}")
        except Exception as e:
            st.error(f"Upload failed: {e}")

# --- Show Sentiment Chart ---
st.header("📊 Sentiment Chart")
if st.button("Show Sentiment Chart"):
    with st.spinner("Loading chart..."):
        try:
            resp = requests.get(f"{API_URL}/sentiment-chart/")
            if resp.ok and resp.headers["content-type"] == "image/png":
                img = Image.open(io.BytesIO(resp.content))
                st.image(img, caption="Sentiment Distribution", use_column_width=True)
            else:
                try:
                    st.error(resp.json().get("message", "No chart available."))
                except Exception:
                    st.error("No chart available.")
        except Exception as e:
            st.error(f"Failed to load chart: {e}")