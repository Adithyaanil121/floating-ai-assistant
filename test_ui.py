import sys
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtTest import QTest
from unittest.mock import patch
import llm_service
import text_extractor
import tts_service
from main import FloatingWidget

def run_tests():
    app = QApplication(sys.argv)
    widget = FloatingWidget()
    widget.show()
    
    print("--- Starting Test 1: UI Initialization ---")
    assert widget.isVisible(), "Widget is not visible"
    assert not widget.menu_container.isVisible(), "Menu should be hidden initially"
    print("Test 1 Passed")
    
    print("--- Starting Test 2: Toggle Menu ---")
    QTest.mouseClick(widget.toggle_btn, Qt.MouseButton.LeftButton)
    assert widget.expanded, "Widget did not register expand"
    assert widget.menu_container.isVisible(), "Menu should be visible now"
    QTest.mouseClick(widget.toggle_btn, Qt.MouseButton.LeftButton)
    assert not widget.expanded, "Widget did not register collapse"
    print("Test 2 Passed")
    
    print("--- Starting Test 3: Explain Button with NO text ---")
    with patch('text_extractor.extract_text', return_value=None):
        QTest.mouseClick(widget.toggle_btn, Qt.MouseButton.LeftButton) # Expand
        QTest.mouseClick(widget.explain_btn, Qt.MouseButton.LeftButton) # Click explain
        assert widget.status_label.text() == "No text selected!", f"Expected 'No text selected!' but got {widget.status_label.text()}"
        print("Test 3 Passed")

    print("--- Starting Test 4: Translate Button with TEXT ---")
    with patch('text_extractor.extract_text', return_value="Bonjour!"), \
         patch('llm_service.translate_and_explain', return_value="Mock Translation"), \
         patch('tts_service.speak') as mock_speak:
         
        QTest.mouseClick(widget.translate_btn, Qt.MouseButton.LeftButton)
        assert widget.status_label.text() == "Done"
        mock_speak.assert_called_with("Mock Translation")
        print("Test 4 Passed")
        
    print("--- Starting Test 5: Explain Button with TEXT ---")
    with patch('text_extractor.extract_text', return_value="Hello World"), \
         patch('llm_service.explain_text', return_value="Mock Explanation"), \
         patch('tts_service.speak') as mock_speak:
         
        QTest.mouseClick(widget.explain_btn, Qt.MouseButton.LeftButton)
        assert widget.status_label.text() == "Done"
        assert widget.chat_container.isVisible(), "Chat container should be visible after explain"
        mock_speak.assert_called_with("Mock Explanation")
        print("Test 5 Passed")
        
    print("--- Starting Test 6: Sending Follow-Up ---")
    with patch('llm_service.ask_follow_up', return_value="Mock Followup"), \
         patch('tts_service.speak') as mock_speak:
         
        widget.chat_input.setText("But why?")
        QTest.mouseClick(widget.send_btn, Qt.MouseButton.LeftButton)
        
        assert widget.chat_input.text() == "", "Input should be cleared after send"
        assert widget.status_label.text() == "Done"
        mock_speak.assert_called_with("Mock Followup")
        print("Test 6 Passed")
        
    print("--- Starting Test 7: Closing Follow-Up ---")
    QTest.mouseClick(widget.close_btn, Qt.MouseButton.LeftButton)
    assert not widget.chat_container.isVisible(), "Chat container should hide when X is clicked"
    print("Test 7 Passed")
    
    print("All tests passed successfully.")
    widget.close()
    app.quit()

if __name__ == '__main__':
    run_tests()
