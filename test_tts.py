import tts_service
import time

print("Testing TTS module...")
tts_service.speak("This is a test of the text to speech interface.")

print("Speaking... waiting 3 seconds before exit.")
time.sleep(3)
print("Done.")
