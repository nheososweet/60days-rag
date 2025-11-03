from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyATN96rHdWVkZdhTpyZ3FNtoYt1AdjHWt0")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="How does AI work?",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
    ),
)
print(response.text)