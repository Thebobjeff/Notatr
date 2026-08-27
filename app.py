import os
import re
from urllib.parse import urlparse
import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
from PIL import Image

# Import your Gemini and Notion services
from core.gemini_service import parse_handwritten_notes, answer_question_about_notes
from core.notion_service import push_meeting_notes_to_notion

# Load environment variables
load_dotenv()

# --- 1. Page Config must come first ---
st.set_page_config(
    page_title="Meeting Notes Digitizer", 
    page_icon="📝", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Custom CSS styling goes right here ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pacifico&family=Roboto:wght@400;700&display=swap');

    /* Hide the top Streamlit header bar */
    header {
        visibility: hidden;
    }

    /* Hide the sidebar collapse/close button */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* Ensure sidebar stays visible and doesn't close */
    [data-testid="stSidebar"] {
        min-width: 300px !important;
        background-color: #000000 !important; /* Sidebar dark background */
    }

    /* Force all text inside sidebar to be white */
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    /* Match the Notion Configuration header style to the main h2 header style */
    [data-testid="stSidebar"] h2 {
        font-family: 'Times New Roman', Times, serif !important;
        font-weight: 900 !important;
        font-size: 1.8rem !important;
        color: #ffffff !important;
    }

    .stApp {
        background-color: #fff8c5;
        background-image: linear-gradient(#f0e6b5 0.1em, transparent 0.1em);
        background-size: 100% 1.8em;
    }
    
    .block-container {
        padding-top: 1rem !important;
        max-width: 1000px;
        margin: 0 auto;
        min-height: 85vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        overflow-y: auto; /* Enables smooth scrolling back inside container */
    }
    
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #000000 !important;
    }

    h2 {
        font-family: 'Times New Roman', Times, serif !important;
        font-weight: 900 !important;
        font-size: 1.8rem !important;
    }
    
    h1 {
        font-family: 'Roboto' !important;
        font-weight: 550 !important;
    }
    
    h1 + p {
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        color: #222222 !important;
        margin-bottom: 2rem !important;
    }

    [data-testid="stFileUploader"], [data-testid="stTextAreaRootElement"] {
        background-color: rgba(0, 0, 0, 0.7) !important;
        border-radius: 10px;
        padding: 10px;
        width: 100%;
    }

    [data-testid="stFileUploader"] *, [data-testid="stTextAreaRootElement"] *, [data-testid="stTextAreaRootElement"] textarea {
        color: #ffffff !important;
    }

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

def extract_notion_id(input_str: str) -> str | None:
    """Extract a 32-character hex Notion ID from a raw ID string or a Notion URL."""
    if not input_str or not isinstance(input_str, str):
        return None

    cleaned_str = input_str.strip()

    # Pattern for 32 hex characters, with optional hyphens
    id_pattern = r"([0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}|[0-9a-f]{32})"
    match = re.search(id_pattern, cleaned_str, re.IGNORECASE)

    if match:
        return match.group(1).replace("-", "")
    return None


def is_valid_notion_input(input_str: str, input_type: str) -> bool:
    """Validate user input based on input type ('URL' or 'Page ID')."""
    notion_id = extract_notion_id(input_str)
    if not notion_id:
        return False

    if input_type == "Page ID":
        return len(notion_id) == 32

    # Accepts notion.so, notion.site, app.notion.com, etc.
    parsed = urlparse(input_str.strip())
    is_valid_scheme = parsed.scheme in ["http", "https"]
    is_valid_domain = "notion" in parsed.netloc.lower()

    return is_valid_scheme and is_valid_domain


# --- Session State Initialization ---
if "notion_destination" not in st.session_state:
    st.session_state["notion_destination"] = os.getenv("NOTION_URL", "")
if "input_type" not in st.session_state:
    st.session_state["input_type"] = "URL"
if "create_new_page" not in st.session_state:
    st.session_state["create_new_page"] = False
if "custom_title" not in st.session_state:
    st.session_state["custom_title"] = ""
    

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Notion Configuration")

    # Mode Selection: Sync to existing vs Create new page
    mode = st.radio(
        "Destination Mode:",
        ["Sync to Existing Location", "Create New Notion Page"],
        index=1 if st.session_state["create_new_page"] else 0,
    )
    st.session_state["create_new_page"] = mode == "Create New Notion Page"

    st.divider()

    # Optional Custom Title Override
    custom_title_input = st.text_input(
        "Custom Meeting Title (Optional)",
        value=st.session_state["custom_title"],
        placeholder="e.g., Q3 Strategy Review",
        help="If provided, overrides the AI-extracted title."
    )
    st.session_state["custom_title"] = custom_title_input.strip()

    if st.session_state["create_new_page"]:
        st.subheader("📄 Create New Page Settings")

        input_type = st.radio(
            "Parent Location Input Method:",
            ["URL", "Page ID"],
            horizontal=True,
            index=0 if st.session_state["input_type"] == "URL" else 1,
        )
        st.session_state["input_type"] = input_type

        parent_input_val = st.text_input(
            f"Parent Notion {input_type}",
            value=st.session_state["notion_destination"],
            placeholder=(
                "https://www.notion.so/..."
                if input_type == "URL"
                else "e.g., 18f28b49..."
            ),
            help=(
                "Paste the URL or Page ID where the new subpage should be created."
            ),
        )

        if parent_input_val and is_valid_notion_input(parent_input_val, input_type):
            st.caption(
                f"✅ Valid Parent ID: `{extract_notion_id(parent_input_val)}`"
            )
        elif parent_input_val:
            st.caption(f"❌ Invalid Parent {input_type} format")

        if st.button("Save Page Creation Settings", use_container_width=True):
            if is_valid_notion_input(parent_input_val, input_type):
                st.session_state["notion_destination"] = parent_input_val
                st.success("Page creation settings saved!")
            else:
                st.error("Please provide a valid Parent location.")

    else:
        st.subheader("🎯 Existing Destination")
        input_type = st.radio(
            "Input Method:",
            ["URL", "Page ID"],
            horizontal=True,
            index=0 if st.session_state["input_type"] == "URL" else 1,
        )
        st.session_state["input_type"] = input_type

        input_val = st.text_input(
            f"Notion {input_type}",
            value=st.session_state["notion_destination"],
            placeholder=(
                "https://www.notion.so/..."
                if input_type == "URL"
                else "e.g., 18f28b49..."
            ),
            help="Paste the URL or Page ID of the target database or page.",
        )

        if input_val and is_valid_notion_input(input_val, input_type):
            st.caption(
                f"✅ Valid Format (ID: `{extract_notion_id(input_val)}`) "
            )
        elif input_val:
            st.caption(f"❌ Invalid {input_type} format")

        if st.button("Save Notion Settings", use_container_width=True):
            if is_valid_notion_input(input_val, input_type):
                st.session_state["notion_destination"] = input_val
                st.success("Settings saved!")
            else:
                st.error("Please enter a valid Notion destination.")

    st.divider()

st.title("📝 Meeting Notes to Notion")
st.write(
    "Upload a picture or PDF of your meeting notes, and AI will extract the"
    " action items to Notion."
)

# Active Target Information
active_dest = st.session_state["notion_destination"]
current_type = st.session_state["input_type"]
active_id = extract_notion_id(active_dest)
create_page_mode = st.session_state["create_new_page"]
custom_title = st.session_state["custom_title"]

if active_dest and is_valid_notion_input(active_dest, current_type):
    if create_page_mode:
        st.info(
            f"🆕 **Mode:** Create new subpages inside parent ID `{active_id}`"
        )
    else:
        st.caption(f"🎯 **Mode:** Sync directly to target ID `{active_id}`")
else:
    st.warning(
        "⚠️ No valid Notion destination configured. Please set up your"
        " settings in the sidebar."
    )

# --- Main Workspace ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("1. Upload Notes")
    uploaded_files = st.file_uploader(
        "Choose images or PDFs of your notes",
        type=["jpg", "jpeg", "png", "pdf"],
        accept_multiple_files=True,
        help="Supports photos (JPG/PNG) and PDF documents.",
    )
    
    if uploaded_files:
        st.write(f"**{len(uploaded_files)} file(s) uploaded:**")
        for file in uploaded_files:
            if file.name.lower().endswith(".pdf"):
                reader = PdfReader(file)
                st.write(f"📄 **{file.name}** ({len(reader.pages)} page[s])")
            else:
                st.image(file, caption=file.name, use_container_width=True)

with col2:
    st.subheader("2. Extract & Sync")
    
    if not uploaded_files:
        st.info("👈 Upload one or more files on the left to get started.")
    elif not active_dest or not is_valid_notion_input(
        active_dest, current_type
    ):
        st.error(
            "👈 Configure a valid Notion URL or Page ID in the sidebar before"
            " processing."
        )
    else:
        st.success(f"{len(uploaded_files)} file(s) ready for processing.")

        target_status = st.selectbox(
            "Default Status in Notion", ["To Do", "In Progress"]
        )

        button_label = (
            "🚀 Create Page & Push Items"
            if create_page_mode
            else "🚀 Process All & Push to Notion"
        )

        if st.button(button_label, type="primary", use_container_width=True):
            with st.status("Processing your notes...", expanded=True) as status:
                generated_urls = []

                for index, file in enumerate(uploaded_files, start=1):
                    st.write(
                        f"🔍 Reading file {index}/{len(uploaded_files)} ({file.name})..."
                    )

                    try:
                        # Branch handling for PDFs vs images
                        if file.name.lower().endswith('.pdf'):
                            reader = PdfReader(file)
                            text_pages = [page.extract_text() or "" for page in reader.pages]
                            pdf_text = "\n".join(text_pages)
                            structured_data = parse_handwritten_notes(pdf_text)
                        else:
                            image = Image.open(file)
                            structured_data = parse_handwritten_notes(image)

                        # Override the AI-generated title if the user provided a specific one
                        if custom_title:
                            new_title = f"{custom_title} ({file.name})"
                            if hasattr(structured_data, 'meeting_title'):
                                structured_data.meeting_title = new_title
                            elif isinstance(structured_data, dict):
                                structured_data['meeting_title'] = new_title

                        # Execute Notion sync using the payload; pass active_id when available
                        notion_url = push_meeting_notes_to_notion(
                            structured_data, target_id=active_id if active_id else None
                        )

                        generated_urls.append((file.name, notion_url))

                    except Exception as e:
                        st.error(f"Failed processing {file.name}: {e}")

                status.update(
                    label="All files processed and pushed to Notion!",
                    state="complete",
                    expanded=False,
                )

            # Render success links
            for name, url in generated_urls:
                st.markdown(f"✅ **{name}**: [View in Notion]({url})")

            if generated_urls:
                st.balloons()