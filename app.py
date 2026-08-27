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
    # Enable multiple file uploads
    uploaded_files = st.file_uploader(
        "Choose images of your notes", 
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        help="Supports clear photos of whiteboards, notebooks, or typed documents."
    )
    
    # Display preview for all uploaded files
    if uploaded_files:
        st.write(f"**{len(uploaded_files)} file(s) uploaded:**")
        for file in uploaded_files:
            st.image(file, caption=file.name, use_container_width=True)

with col2:
    st.subheader("2. Extract & Sync")
    
    if not uploaded_files:
        st.info("👈 Upload one or more images on the left to get started.")
    else:
        st.success(f"{len(uploaded_files)} image(s) ready for processing.")
        
        target_status = st.selectbox("Default Status in Notion", ["To Do", "In Progress"])
        
        if st.button("🚀 Process All & Push to Notion", type="primary", use_container_width=True):
            with st.status("Processing your notes...", expanded=True) as status:
                # Loop through each uploaded file
                for index, file in enumerate(uploaded_files, start=1):
                    st.write(f"🔍 Reading image {index}/{len(uploaded_files)} ({file.name})...")
                    # action_items = extract_action_items(file)
                    
                    st.write(f"📤 Exporting items from {file.name} to Notion...")
                    # send_to_notion(action_items)
                
                status.update(label="All files processed and pushed to Notion!", state="complete", expanded=False)
            
            st.balloons()

    additional_notes = st.text_area(
    "Additional context or instructions for AI (Optional)",
    placeholder=(
        "Type any special instructions, project tags, or context you want"
        " included..."
    ),
)