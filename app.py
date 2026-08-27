import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Meeting Notes Digitizer", page_icon="📝")

st.title("📝 Meeting Notes to Notion")
st.write("Upload a picture of your handwritten meeting notes, and AI will extract the action items to Notion.")

# uploaded_file = st.file_uploader("Upload meeting notes...", type=["jpg", "jpeg", "png"])

# if uploaded_file is not None:
#     st.image(uploaded_file, caption="Uploaded Notes", use_container_width=True)
    
#     if st.button("Extract Action Items"):
#         st.info("Gemini vision processing will happen here...")
#         # TODO: Call core.gemini_service.py
#         # TODO: Push results via core.notion_service.py

# --- Main Workspace ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("1. Upload Notes")
    uploaded_file = st.file_uploader(
        "Choose an image of your notes", 
        type=["jpg", "jpeg", "png"],
        help="Supports clear photos of whiteboards, notebooks, or typed documents."
    )
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Preview", use_container_width=True)

with col2:
    st.subheader("2. Extract & Sync")
    
    if uploaded_file is None:
        st.info("👈 Upload an image on the left to get started.")
    else:
        st.success("Image uploaded ready for processing.")
        
        # Option to select target database or tags
        target_status = st.selectbox("Default Status in Notion", ["To Do", "In Progress"])
        
        if st.button("🚀 Process & Push to Notion", type="primary", use_container_width=True):
            with st.status("Processing your notes...", expanded=True) as status:
                st.write("🔍 Reading image with Gemini Vision...")
                # TODO: Call gemini_service
                
                st.write("📌 Extracting action items...")
                # TODO: Format items
                
                st.write("📤 Exporting to Notion...")
                # TODO: Call notion_service
                
                status.update(label="Complete! Action items added to Notion.", state="complete", expanded=False)
            
            st.balloons()