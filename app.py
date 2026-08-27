import io
from dotenv import load_dotenv
from google import genai
from PIL import Image
from pydantic import BaseModel, Field
import streamlit as st

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Meeting Notes Digitizer", page_icon="📝")

# --- PASTE CSS HERE ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #9AC769;
        color: #f3f4f6;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("📝 Meeting Notes to Notion")
st.write(
    "Upload a picture of your handwritten meeting notes, and AI will extract"
    " the action items to Notion."
)

uploaded_file = st.file_uploader("Upload meeting notes...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Notes", use_container_width=True)
    
    if st.button("Extract Action Items"):
        st.info("Gemini vision processing will happen here...")
        # TODO: Call core.gemini_service.py
        # TODO: Push results via core.notion_service.py