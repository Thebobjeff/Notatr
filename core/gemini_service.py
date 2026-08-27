 
from google import genai
from PIL import Image
from core.schemas import MeetingPayload


def get_gemini_client(api_key: str = "") -> genai.Client:
    token = api_key.strip() if api_key else ""
    if not token:
        raise ValueError("A Gemini API key is required.")
    return genai.Client(api_key=token)


def parse_handwritten_notes(
    image: Image.Image, api_key: str | None = None
) -> MeetingPayload:
    """
    Takes a PIL Image of handwritten notes and extracts structured meeting minutes
    using gemini-3.7-flash.
    """
    prompt = (
        "Transcribe and convert these handwritten meeting notes into structured minutes. "
        "Extract key decisions, summarize discussion topics, and isolate actionable tasks. "
        "If diagrams/arrows are visible, convert them to Mermaid.js syntax."
    )
    
    # This is where you specify the faster flash model
    client = get_gemini_client(api_key)
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[image, prompt],
        config=dict(
            response_mime_type="application/json",
            response_schema=MeetingPayload,
            temperature=0.2, # Low temperature for more factual extraction
        ),
    )
    
    # Validate and return the response as a Python object based on your schema
    return MeetingPayload.model_validate_json(response.text)

def answer_question_about_notes(
    payload: MeetingPayload, question: str, api_key: str | None = None
) -> str:
    """
    Uses Gemini to answer user questions based strictly on the extracted meeting notes.
    """
    # Convert the parsed pydantic model back to a clean JSON string for the prompt
    context_data = payload.model_dump_json(indent=2)
    
    prompt = (
        f"You are a helpful assistant analyzing meeting notes.\n"
        f"Here are the details of the meeting:\n{context_data}\n\n"
        f"Answer the following user question based ONLY on the meeting notes above. "
        f"Keep your answer concise and helpful.\n"
        f"User Question: {question}"
    )
    
    # We can reuse the flash model for blazing fast chat responses
    client = get_gemini_client(api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    return response.text