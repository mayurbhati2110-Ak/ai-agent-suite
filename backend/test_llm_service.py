from app.services.llm_service import LLMService


print("Initializing LLM Service...")

llm = LLMService()

print("LLM Service initialized successfully.")
print(f"Model route: {llm.model}")


try:
    response = llm.chat(
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: LLM Service is working"
            }
        ],
        temperature=0
    )

    print("\nResponse:")
    print(response)

except Exception as error:
    print("\nLLM Service test failed:")
    print(error)