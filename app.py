import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

    /* Hide the top Streamlit header bar */
    header {
        visibility: hidden;
    }

    .stApp {
        background-color: #fff8c5;
        background-image: linear-gradient(#f0e6b5 0.1em, transparent 0.1em);
        background-size: 100% 1.8em;
    }
    
    /* Move main block / top padding up and enable full-height flex container for vertical centering */
    .block-container {
        padding-top: 1rem !important;
        max-width: 1000px;
        margin: 0 auto;
        min-height: 85vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    h1, h2, h3, h4, h5, h6, p, span, label {
    
        color: #000000 !important;
    }

    /* Give specific subheaders (h2) Times New Roman font */
    h2 {
        font-family: 'Pacifico' !important;
        font-weight: 500 !important;
    }
    

    h1 {
        font-family: 'Pacifico', cursive !important;
        font-weight: 700 !important;
    }
    
    /* Add distance/margin below the main title and its caption description */
    h1 + p {
        margin-bottom: 3rem !important;
    }

    /* Make file uploader and text area boxes black with 70% opacity */
    [data-testid="stFileUploader"], [data-testid="stTextAreaRootElement"] {
        background-color: rgba(0, 0, 0, 0.7) !important;
        border-radius: 10px;
        padding: 10px;
        width: 100%;
    }

    /* Make inner text/labels inside those transparent black boxes white */
    [data-testid="stFileUploader"] *, [data-testid="stTextAreaRootElement"] *, [data-testid="stTextAreaRootElement"] textarea {
        color: #ffffff !important;
    }

    /* Style the info box to be black (replacing the gray box) with rounded corners and white text */
    .stAlert {
        background-color: #000000 !important;
        border: 1px solid #000000 !important;
        border-radius: 10px !important;
    }
    
    .stAlert * {
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.set_page_config(page_title="Meeting Notes Digitizer", page_icon="📝")

st.title("📝 Meeting Notes to Notion")
st.write(
    "Upload a picture of your handwritten meeting notes, and AI will extract"
    " the action items to Notion."
)

# --- Main Workspace ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
  st.subheader("1. Upload Notes")
  # Enable multiple file uploads
  uploaded_files = st.file_uploader(
      "Choose images of your notes",
      type=["jpg", "jpeg", "png"],
      accept_multiple_files=True,
      help="Supports clear photos of whiteboards, notebooks, or typed documents.",
  )

  # Display preview for all uploaded files
  if uploaded_files:
    st.write(f"**{len(uploaded_files)} file(s) uploaded:**")
    for file in uploaded_files:
      st.image(file, caption=file.name, use_container_width=True)

with col2:
  st.subheader("2. Extract & Sync")

  # Added text box for custom instructions
  additional_notes = st.text_area(
      "Additional context or instructions for AI (Optional)",
      placeholder=(
          "Type any special instructions, project tags, or context you want"
          " included..."
      ),
  )

  if not uploaded_files:
    st.info("👈 Upload one or more images on the left to get started.")
  else:
    st.success(f"{len(uploaded_files)} image(s) ready for processing.")

    target_status = st.selectbox(
        "Default Status in Notion", ["To Do", "In Progress"]
    )

    if st.button(
        "🚀 Process All & Push to Notion",
        type="primary",
        use_container_width=True,
    ):
      with st.status("Processing your notes...", expanded=True) as status:
        # Loop through each uploaded file
        for index, file in enumerate(uploaded_files, start=1):
          st.write(
              f"🔍 Reading image {index}/{len(uploaded_files)} ({file.name})..."
          )
          # action_items = extract_action_items(file, additional_notes)

          st.write(f"📤 Exporting items from {file.name} to Notion...")
          # send_to_notion(action_items)

        status.update(
            label="All files processed and pushed to Notion!",
            state="complete",
            expanded=False,
        )

      st.balloons()