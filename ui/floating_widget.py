from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QApplication
from PyQt6.QtCore import Qt, QTimer, QEvent
from core import llm_service
from core import text_extractor
from core import tts_service

class FloatingWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Transparent, frameless window, always on top
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setGeometry(100, 100, 200, 300)
        
        self.old_pos = None
        self.expanded = False
        
        self.init_ui()
        
    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)
        
        # Main toggle button
        self.toggle_btn = QPushButton("M") # Mobizen-like
        self.toggle_btn.setFixedSize(30, 30)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_inactive_style()
        
        # Install event filter to handle dragging on the button itself
        self.toggle_btn.installEventFilter(self)
        self.is_dragging = False
        self.drag_start_pos = None
        
        # Container for the buttons
        self.menu_container = QWidget()
        self.menu_layout = QVBoxLayout()
        self.menu_layout.setContentsMargins(0, 0, 0, 0)
        self.menu_layout.setSpacing(5)
        self.menu_container.setLayout(self.menu_layout)
        
        self.explain_btn = QPushButton("Start Explain")
        self.translate_btn = QPushButton("Start Translation")
        
        style = """
            QPushButton {
                background-color: rgba(50, 50, 50, 220); 
                color: white; 
                border-radius: 15px; 
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(70, 70, 70, 240);
            }
        """
        self.explain_btn.setStyleSheet(style)
        self.translate_btn.setStyleSheet(style)
        
        self.explain_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.translate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.explain_btn.clicked.connect(self.on_explain_clicked)
        self.translate_btn.clicked.connect(self.on_translate_clicked)
        
        self.menu_layout.addWidget(self.explain_btn)
        self.menu_layout.addWidget(self.translate_btn)
        
        self.menu_container.hide()
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: white; font-weight: bold; background-color: rgba(0, 0, 0, 150); border-radius: 5px; padding: 5px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.hide()

        # Follow-up Chat Container
        self.chat_container = QWidget()
        self.chat_layout = QHBoxLayout()
        self.chat_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_container.setLayout(self.chat_layout)
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Follow-up question...")
        self.chat_input.setStyleSheet("background-color: white; color: black; border-radius: 5px; padding: 5px;")
        
        self.send_btn = QPushButton("Send")
        self.send_btn.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 5px; padding: 5px; font-weight: bold;")
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.close_btn = QPushButton("X")
        self.close_btn.setStyleSheet("background-color: #f44336; color: white; border-radius: 5px; padding: 5px; font-weight: bold;")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setFixedWidth(30)
        
        self.chat_layout.addWidget(self.chat_input)
        self.chat_layout.addWidget(self.send_btn)
        self.chat_layout.addWidget(self.close_btn)
        
        self.chat_container.hide()
        
        self.send_btn.clicked.connect(self.on_send_clicked)
        self.chat_input.returnPressed.connect(self.on_send_clicked)
        self.close_btn.clicked.connect(self.on_close_clicked)

        self.layout.addWidget(self.toggle_btn, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.menu_container, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.chat_container, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        self.layout.addStretch()

    def set_inactive_style(self):
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                border-radius: 15px; 
                background-color: rgba(255, 94, 94, 128); 
                color: rgba(255, 255, 255, 128); 
                font-weight: bold; 
                font-size: 14px;
                border: 1px solid rgba(255, 255, 255, 128);
            }
            QPushButton:hover {
                background-color: rgba(255, 59, 59, 255);
                color: rgba(255, 255, 255, 255);
                border: 1px solid rgba(255, 255, 255, 255);
            }
        """)
        
    def set_active_style(self):
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                border-radius: 15px; 
                background-color: rgba(255, 94, 94, 255); 
                color: rgba(255, 255, 255, 255); 
                font-weight: bold; 
                font-size: 14px;
                border: 1px solid rgba(255, 255, 255, 255);
            }
        """)

    def toggle_menu(self):
        self.expanded = not self.expanded
        self.menu_container.setVisible(self.expanded)
        if self.expanded:
            self.set_active_style()
        else:
            self.set_inactive_style()

    def eventFilter(self, obj, event):
        if obj == self.toggle_btn:
            if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                self.is_dragging = False
                self.drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                # Do NOT accept the event here so the button still gets the press styling if it wasn't a drag
                return False 
                
            elif event.type() == QEvent.Type.MouseMove:
                if self.drag_start_pos is not None:
                    # Check if moved far enough to be considered a drag
                    current_global_pos = event.globalPosition().toPoint()
                    diff = current_global_pos - self.drag_start_pos - self.frameGeometry().topLeft()
                    
                    # If moved more than 3 pixels, it's a drag
                    if diff.manhattanLength() > 3 or self.is_dragging:
                        self.is_dragging = True
                        self.move(current_global_pos - self.drag_start_pos)
                        return True # Consume to prevent hover styling issues during drag
                        
            elif event.type() == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
                if self.is_dragging:
                    self.is_dragging = False
                    self.drag_start_pos = None
                    return True # Consume release so it doesn't trigger a click
                else:
                    self.drag_start_pos = None
                    self.toggle_menu() # It was a clean click
                    return True # Consume so QPushButton doesn't double-fire
                    
        return super().eventFilter(obj, event)

    # Keep standard drag capability if clicking on the blank translucent space around the menu
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.old_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None
            event.accept()
            
    def show_status(self, text):
        self.status_label.setText(text)
        self.status_label.show()
        QTimer.singleShot(3000, self.status_label.hide)

    def on_explain_clicked(self):
        self.show_status("Extracting...")
        QApplication.processEvents() # Force UI update before blocking operations
        # Hide widget temporarily so it doesn't get in the way of window focus
        self.hide()
        text = text_extractor.extract_text()
        self.show()
        
        if not text:
            self.show_status("No text selected!")
            return
            
        self.show_status("Thinking...")
        QApplication.processEvents()
        
        response = llm_service.explain_text(text)
        
        self.show_status("Speaking...")
        QApplication.processEvents()
        
        tts_service.speak(response)
        self.show_status("Done")
        self.chat_container.show()
        self.menu_container.hide()
        self.expanded = False

    def on_translate_clicked(self):
        self.show_status("Extracting...")
        QApplication.processEvents()
        self.hide()
        text = text_extractor.extract_text()
        self.show()
        
        if not text:
            self.show_status("No text selected!")
            return
            
        self.show_status("Thinking...")
        QApplication.processEvents()
        
        response = llm_service.translate_and_explain(text)
        
        self.show_status("Speaking...")
        QApplication.processEvents()
        
        tts_service.speak(response)
        self.show_status("Done")
        self.chat_container.show()
        self.menu_container.hide()
        self.expanded = False
        self.set_active_style() # Keep it solid while chat is open
        
    def on_close_clicked(self):
        self.chat_container.hide()
        llm_service.clear_history()
        self.status_label.hide()
        self.set_inactive_style() # Revert to translucent
        
    def on_send_clicked(self):
        question = self.chat_input.text().strip()
        if not question:
            return
            
        self.chat_input.clear()
        
        self.show_status("Thinking...")
        QApplication.processEvents()
        
        response = llm_service.ask_follow_up(question)
        
        self.show_status("Speaking...")
        QApplication.processEvents()
        
        tts_service.speak(response)
        self.show_status("Done")

