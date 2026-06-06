import os
from google import genai
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("GOOGLE_API_KEY")

print("Initializing Client...")
client = genai.Client(api_key=api_key)

models_to_test = [
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
    "gemini-2.5-flash-lite",
]

for model_name in models_to_test:
    print(f"\nTesting model: {model_name}")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents="Say 'yes' if you can read this.",
        )
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Failed: {e}")
