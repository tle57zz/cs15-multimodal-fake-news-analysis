from llm_models.chat_service import chat_with_model

result = chat_with_model("Explain quantum computing in simple terms.")

print(result["answer"])
