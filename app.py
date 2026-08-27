import os
import re
from urllib.parse import urlparse
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Meeting Notes Digitizer", page_icon="📝")


def extract_notion_id(input_str: str) -> str | None:
    """Extract a 32-character hex Notion ID from a raw ID string or a Notion URL."""
    if not input_str or not isinstance(input_str, str):
        return None

    cleaned_str = input_str.strip()

    # Pattern for 32 hex characters, with optional hyphens
    id_pattern = r"([0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}|[0-9a-f]{32})"
    match = re.search(id_pattern, cleaned_str, re.IGNORECASE)

    if match:
        # Return ID without hyphens
        return match.group(1).replace("-", "")
    return None


def is_valid_notion_input(input_str: str, input_type: str) -> bool:
    """Validate user input based on input type ('URL' or 'Page ID')."""
    notion_id = extract_notion_id(input_str)
    if not notion_id:
        return False

    if input_type == "Page ID":
        return len(notion_id) == 32

    # If URL, check domain in addition to finding a valid ID
    parsed = urlparse(input_str.strip())
    is_valid_scheme = parsed.scheme in ["http", "https"]
    is_valid_domain = parsed.netloc.endswith(
        "notion.so"
    ) or parsed.netloc.endswith("notion.site")

    return is_valid_scheme and is_valid_domain


# --- Session State Initialization ---
if "notion_destination" not in st.session_state:
    st.session_state["notion_destination"] = os.getenv("NOTION_URL", "")
if "input_type" not in st.session_state:
    st.session_state["input_type"] = "URL"

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Notion Configuration")

    # Toggle between URL and Page ID
    input_type = st.radio(
        "Input Method:",
        ["URL", "Page ID"],
        horizontal=True,
        index=0 if st.session_state["input_type"] == "URL" else 1,
    )
    st.session_state["input_type"] = input_type

    placeholder_text = (
        "https://www.notion.so/..."
        if input_type == "URL"
        else "e.g., 18f28b49a15a80d49e7fc123456789ab"
    )

    input_val = st.text_input(
        f"Notion {input_type}",
        value=st.session_state["notion_destination"],
        placeholder=placeholder_text,
        help=(
            "Paste the full URL of your Notion page/database"
            if input_type == "URL"
            else "Paste the 32-character Notion Page or Database ID"
        ),
    )

    # Live validation feedback
    if input_val:
        if is_valid_notion_input(input_val, input_type):
            extracted_id = extract_notion_id(input_val)
            st.caption(f"✅ Valid format (Extracted ID: `{extracted_id}`) ")
        else:
            st.caption(f"❌ Invalid Notion {input_type} format")

    if st.button("Save Notion Settings", use_container_width=True):
        if is_valid_notion_input(input_val, input_type):
            st.session_state["notion_destination"] = input_val
            st.success(f"Notion {input_type} saved!")
        else:
            st.error(f"Please enter a valid Notion {input_type} before saving.")

    st.divider()

st.title("📝 Meeting Notes to Notion")
st.write(
    "Upload a picture of your handwritten meeting notes, and AI will extract"
    " the action items to Notion."
)

# Display active target status
active_dest = st.session_state["notion_destination"]
current_type = st.session_state["input_type"]
active_id = extract_notion_id(active_dest)

if active_dest and is_valid_notion_input(active_dest, current_type):
    st.caption(f"🎯 Target Page/Database ID: `{active_id}`")
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
        "Choose images of your notes",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        help=(
            "Supports clear photos of whiteboards, notebooks, or typed"
            " documents."
        ),
    )

    if uploaded_files:
        st.write(f"**{len(uploaded_files)} file(s) uploaded:**")
        for file in uploaded_files:
            st.image(file, caption=file.name, use_container_width=True)

with col2:
    st.subheader("2. Extract & Sync")

    if not uploaded_files:
        st.info("👈 Upload one or more images on the left to get started.")
    elif not active_dest or not is_valid_notion_input(
        active_dest, current_type
    ):
        st.error(
            "👈 Configure a valid Notion URL or Page ID in the sidebar before"
            " processing."
        )
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
            with st.status(
                "Processing your notes...", expanded=True
            ) as status:
                for index, file in enumerate(uploaded_files, start=1):
                    st.write(
                        f"🔍 Reading image {index}/{len(uploaded_files)}"
                        f" ({file.name})..."
                    )
                    # action_items = extract_action_items(file)

                    st.write(
                        f"📤 Exporting items from {file.name} to Notion ID"
                        f" `{active_id}`..."
                    )
                    # send_to_notion(action_items, target_id=active_id)

                status.update(
                    label="All files processed and pushed to Notion!",
                    state="complete",
                    expanded=False,
                )

            st.balloons()