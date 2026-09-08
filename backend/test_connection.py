import os

from dotenv import load_dotenv
from openai import OpenAI


# Load values from .env
load_dotenv(dotenv_path=".env", override=True)
print("Loaded model:", repr(os.getenv("LLM_MODEL")))

api_key = os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_BASE_URL")
model = os.getenv("LLM_MODEL")


print("Testing FreeLLMAPI connection...")
print(f"Base URL: {base_url}")
print(f"Model route: {model}")


client = OpenAI(
    api_key=api_key,
    base_url=base_url
)


try:

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: Connection successful"
            }
        ],
        temperature=0
    )

    print("\nResponse:")
    print(response.choices[0].message.content)


except Exception as error:

    print("\nConnection failed:")
    print(error)