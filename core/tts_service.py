import pyttsx3
import threading

# Global references
_speech_thread = None
_engine = None

def _speak_worker(text):
    global _engine
    
    # Initialize a new engine inside this thread.
    # On Windows SAPI, COM objects must be instantiated in the thread they are used.
    _engine = pyttsx3.init()
    
    # You can adjust properties here such as rate and volume
    # _engine.setProperty('rate', 150)
    
    _engine.say(text)
    
    try:
        _engine.runAndWait()
    except Exception:
        pass
    finally:
        _engine = None

def speak(text):
    """
    Speaks the given text using the system's default text-to-speech engine.
    Runs in a separate thread to avoid freezing the UI, and avoids multiprocessing
    to prevent duplicate window spawns on Windows.
    """
    global _speech_thread
    
    # Stop any currently playing speech before starting a new one
    stop_speaking()
    
    # Start a new daemon thread for the speech
    _speech_thread = threading.Thread(target=_speak_worker, args=(text,), daemon=True)
    _speech_thread.start()

def stop_speaking():
    """
    Attempts to immediately stop the TTS engine if it is currently speaking.
    """
    global _speech_thread, _engine
    
    if _engine is not None:
        try:
            _engine.stop()
        except Exception:
            pass # SAPI might throw cross-thread COM errors, ignore them.

    if _speech_thread is not None and _speech_thread.is_alive():
        # Wait a tiny bit, but don't block the UI thread waiting for the thread to die
        _speech_thread.join(timeout=0.1)
        _speech_thread = None
