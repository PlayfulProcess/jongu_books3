import os
import openai
from dotenv import load_dotenv

# Load environment variables from the root directory
load_dotenv(dotenv_path='../.env')

api_key = os.getenv("OPENAI_API_KEY")

def test_openai_api_direct_read():
    if api_key:
        print(f"SUCCESS: API key found in .env. Key starts with: {api_key[:10]}...")
    else:
        print("ERROR: API key not found in .env file.")

if __name__ == "__main__":
    test_openai_api_direct_read() 