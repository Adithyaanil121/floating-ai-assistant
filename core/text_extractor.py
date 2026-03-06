import pyautogui
import pyperclip
import time

def extract_text():
    """
    Simulates Ctrl+C to copy selected text from the active window,
    then retrieves it from the clipboard.
    """
    # Save the current clipboard content to restore it later if needed,
    # or just clear it to ensure we get fresh text.
    original_clipboard = pyperclip.paste()
    pyperclip.copy('')
    
    # Give a tiny delay to ensure the OS has registered our widget hiding
    time.sleep(0.5)

    # Simulate Ctrl+C
    pyautogui.hotkey('ctrl', 'c')
    
    # Wait a bit for the clipboard to update
    time.sleep(0.5)
    
    copied_text = pyperclip.paste()
    
    # If nothing was copied, it might mean nothing was selected.
    if not copied_text or copied_text.isspace():
        return None
        
    return copied_text.strip()
