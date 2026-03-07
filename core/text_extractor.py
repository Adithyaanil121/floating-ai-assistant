import pyautogui
import pyperclip
import time

def extract_text():
    """
    Simulates Ctrl+C to copy selected text from the active window,
    then retrieves it from the clipboard.
    """
    try:
        # Save the current clipboard content to restore it later if needed,
        # or just clear it to ensure we get fresh text.
        try:
            original_clipboard = pyperclip.paste()
        except Exception:
            original_clipboard = ""
            
        pyperclip.copy('')
        
        # Give a tiny delay to ensure the OS has registered our widget hiding
        time.sleep(0.2)

        # Simulate Ctrl+C
        pyautogui.hotkey('ctrl', 'c')
        
        # Wait a bit for the clipboard to update
        time.sleep(0.1)
        
        try:
            copied_text = pyperclip.paste()
        except Exception:
            copied_text = ""
            
        # If nothing was copied, it might mean nothing was selected.
        if not copied_text or copied_text.isspace():
            return None
            
        return copied_text.strip()
    except Exception as e:
        print(f"Extraction error: {str(e)}")
        return None
