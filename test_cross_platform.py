import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path so we can import core.text_extractor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core import text_extractor

class TestCrossPlatformExtraction(unittest.TestCase):

    @patch('core.text_extractor.pyautogui.hotkey')
    @patch('core.text_extractor.pyperclip.paste')
    @patch('core.text_extractor.pyperclip.copy')
    @patch('core.text_extractor.sys.platform', 'win32')
    def test_windows_copy_shortcut(self, mock_copy, mock_paste, mock_hotkey):
        mock_paste.side_effect = ["old_clip", "new_text"]
        result = text_extractor.extract_text()
        mock_hotkey.assert_called_with('ctrl', 'c')
        self.assertEqual(result, "new_text")

    @patch('core.text_extractor.pyautogui.hotkey')
    @patch('core.text_extractor.pyperclip.paste')
    @patch('core.text_extractor.pyperclip.copy')
    @patch('core.text_extractor.sys.platform', 'darwin')
    def test_mac_copy_shortcut(self, mock_copy, mock_paste, mock_hotkey):
        mock_paste.side_effect = ["old_clip", "new_text"]
        result = text_extractor.extract_text()
        mock_hotkey.assert_called_with('command', 'c')
        self.assertEqual(result, "new_text")

    @patch('core.text_extractor.pyautogui.hotkey')
    @patch('core.text_extractor.pyperclip.paste')
    @patch('core.text_extractor.pyperclip.copy')
    @patch('core.text_extractor.sys.platform', 'linux')
    def test_linux_copy_shortcut(self, mock_copy, mock_paste, mock_hotkey):
        mock_paste.side_effect = ["old_clip", "new_text"]
        result = text_extractor.extract_text()
        mock_hotkey.assert_called_with('ctrl', 'c')
        self.assertEqual(result, "new_text")

if __name__ == '__main__':
    unittest.main()
