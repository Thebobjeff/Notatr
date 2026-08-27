import streamlit as st
from dotenv import load_dotenv
import os
from PIL import Image

# Import your Gemini and Notion services
from core.gemini_service import parse_handwritten_notes, answer_question_about_notes
from core.notion_service import push_meeting_notes_to_notion

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Meeting Notes Digitizer", page_icon="📝", layout="wide")

st.title("📝 Meeting Notes to Notion")
st.write("Upload a picture of your handwritten meeting notes, and AI will extract the action items to Notion.")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("1. Upload Notes")
    uploaded_files = st.file_uploader(
        "Choose images of your notes", 
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        help="Supports clear photos of whiteboards, notebooks, or typed documents."
    )
    
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
                generated_urls = []
                
                for index, file in enumerate(uploaded_files, start=1):
                    st.write(f"🔍 Reading image {index}/{len(uploaded_files)} ({file.name})...")
                    try:
                        # Convert byte stream to PIL Image
                        image = Image.open(file)
                        
                        # Execute Gemini extraction
                        structured_data = parse_handwritten_notes(image)
                        
                        st.write(f"📤 Exporting items from {file.name} to Notion...")
                        
                        # Execute Notion sync 
                        notion_url = push_meeting_notes_to_notion(structured_data)
                        generated_urls.append((file.name, notion_url))
                        
                    except Exception as e:
                        st.error(f"Failed processing {file.name}: {e}")
                
                status.update(label="Batch processing complete!", state="complete", expanded=False)
            
            # Render success links
            for name, url in generated_urls:
                st.markdown(f"✅ **{name}**: [View in Notion]({url})")
                
            if generated_urls:
                st.balloons()