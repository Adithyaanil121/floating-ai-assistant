import pyttsx3
import multiprocessing

# Global reference to the current speech process
_speech_process = None

def _speak_worker(text):
    """
    Runs in a dedicated process to speak the text.
    Isolated from the main PyQT thread so it can be killed safely.
    """
    engine = pyttsx3.init()
    # You can adjust properties here such as rate and volume
    # engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()

def speak(text):
    """
    Speaks the given text using the system's default text-to-speech engine.
    Runs in a separate process to allow immediate cancellation.
    """
    global _speech_process
    
    # Stop any currently playing speech before starting a new one
    stop_speaking()
    
    # Start a new process for the speech
    _speech_process = multiprocessing.Process(target=_speak_worker, args=(text,), daemon=True)
    _speech_process.start()

def stop_speaking():
    """
    Immediately stops the TTS engine if it is currently speaking.
    """
    global _speech_process
    if _speech_process is not None and _speech_process.is_alive():
        _speech_process.terminate()
        _speech_process.join(timeout=0.5)
        _speech_process = None
