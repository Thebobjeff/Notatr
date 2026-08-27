from dotenv import load_dotenv  # 1. Import load_dotenv
from google import genai

from dotenv import load_dotenv  # 1. Import load_dotenv

# The client automatically picks up GEMINI_API_KEY from your .env file
client = client = genai.Client(api_key="AQ.Ab8RN6Lgg_gJT_sF3bm-HCNFSX7M8Eiz-_XQ4WhguJepNugxzQ")

response = client.interactions.create(
    model="gemini-3.7-flash",
    input="How do I make the app.py prettier?",
)

print(response.output_text)