import text_extractor
import time

print("Please select some text in any window...")
print("You have 3 seconds...")
time.sleep(3)

print("Extracting...")
text = text_extractor.extract_text()

print(f"\nExtracted Text:\n{text}")
