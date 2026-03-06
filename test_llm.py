import llm_service

print("Testing LLM Explain...")
response = llm_service.explain_text("The quick brown fox jumps over the lazy dog.")
print(f"Explain Response:\n{response}\n")

print("Testing LLM Translate & Explain...")
response = llm_service.translate_and_explain("El camarón que se duerme, se lo lleva la corriente.")
print(f"Translate Response:\n{response}\n")
