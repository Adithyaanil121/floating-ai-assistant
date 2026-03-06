import pyttsx3
import threading

def speak(text):
    """
    Speaks the given text using the system's default text-to-speech engine.
    Runs in a separate thread to avoid blocking the main UI.
    """
    def _speak_thread():
        engine = pyttsx3.init()
        # You can adjust properties here such as rate and volume
        # engine.setProperty('rate', 150)
        engine.say(text)
        engine.runAndWait()

    thread = threading.Thread(target=_speak_thread, daemon=True)
    thread.start()
