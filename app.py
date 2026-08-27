import streamlit as st
from dotenv import load_dotenv
import os
from PIL import Image

# Import your Gemini service
from core.gemini_service import parse_handwritten_notes

# Load environment variables
load_dotenv()

# Set layout to wide for the side-by-side view
st.set_page_config(page_title="Meeting Notes Digitizer", page_icon="📝", layout="wide")

st.title("📝 Meeting Notes to Notion")
st.write("Upload a picture of your handwritten meeting notes, and AI will extract the action items.")

# Create a 2-column layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Notes")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Convert the uploaded file to a PIL Image
        image = Image.open(uploaded_file)
        st.image(image, caption="Original Handwritten Notes", use_container_width=True)
        
        if st.button("Extract Action Items", type="primary"):
            with col2:
                with st.spinner("Analyzing handwriting with Gemini 2.5 Flash..."):
                    try:
                        # Call the backend service
                        structured_data = parse_handwritten_notes(image)
                        
                        # Store in session state so it doesn't disappear if the app reruns
                        st.session_state.meeting_data = structured_data
                    except Exception as e:
                        st.error(f"An API error occurred: {e}")

# Render the extracted data in the second column
with col2:
    st.subheader("2. Extracted Minutes")
    
    # Check if we have data stored in the session state
    if "meeting_data" in st.session_state:
        data = st.session_state.meeting_data
        
        st.header(data.meeting_title)
        if data.date_detected:
            st.caption(f"Date: {data.date_detected}")
            
        st.markdown("### Executive Summary")
        st.write(data.executive_summary)
        
        st.markdown("### Key Discussion Points")
        for point in data.key_discussion_points:
            st.markdown(f"- {point}")
            
        st.markdown("### Decisions Made")
        for decision in data.decisions_made:
            st.markdown(f"- {decision}")
            
        st.markdown("### ✅ Action Items")
        for item in data.action_items:
            # Render interactive checkboxes for tasks
            st.checkbox(f"**{item.task}** (Assignee: {item.assignee}, Due: {item.deadline})")
            
        if data.diagram_mermaid:
            st.markdown("### Diagram Detected")
            st.code(data.diagram_mermaid, language="mermaid")
            
        st.divider()
        if st.button("🚀 Push to Notion"):
            st.info("Notion integration coming next!")
            # TODO: Call core.notion_service.py