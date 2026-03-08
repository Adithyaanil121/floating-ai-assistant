from core import llm_service

print("--- Testing Cryptography Explanation (Teacher Mode) ---")
test_text = "Cryptography is the practice and study of techniques for secure communication in the presence of adversarial behavior. More generally, cryptography is about constructing and analyzing protocols that prevent third parties or the public from reading private messages."

response = llm_service.explain_text(test_text)
print(f"Teacher Explanation:\n{response}\n")

with open("test_cryptography_out.txt", "w", encoding="utf-8") as f:
    f.write(response)

print("Result saved to test_cryptography_out.txt")
