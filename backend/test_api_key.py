import os
from dotenv import load_dotenv
import openai

# Load environment variables from the root directory
load_dotenv(dotenv_path='../.env')

# Configure OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

print(f"API Key loaded: {openai.api_key[:10]}..." if openai.api_key else "No API key found")

if not openai.api_key:
    print("ERROR: No API key found!")
    exit(1)

try:
    # Test with a simple API call
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Say 'Hello, API key is working!'"}
        ],
        max_tokens=10
    )
    
    print("SUCCESS: API key is working!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"ERROR: API call failed: {e}") 