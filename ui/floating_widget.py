from PyQt6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QHBoxLayout, 
                               QLabel, QLineEdit, QApplication, QTextEdit, QGraphicsDropShadowEffect, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QTimer, QEvent, QPropertyAnimation, QEasingCurve, QSize, pyqtProperty, QRectF
from PyQt6.QtGui import QColor, QFont, QIcon, QPixmap, QPainter
import os
import sys

def get_asset_path(filename):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        # Resolve to project root rather than `ui` folder
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, 'assets', filename)

from core import llm_service
from core import text_extractor
from core import tts_service


# ── Color Palette ──────────────────────────────────────────────
COLORS = {
    'primary':      '#8B5CF6',   # purple
    'primary_end':  '#EC4899',   # pink
    'accent':       '#10B981',   # emerald
    'accent_dark':  '#059669',   # darker emerald
    'danger':       '#EF4444',   # red
    'danger_dark':  '#DC2626',   # darker red
    'surface':      'rgba(30, 30, 40, 220)',
    'surface_light':'rgba(45, 45, 60, 220)',
    'text':         '#F1F5F9',
    'text_muted':   '#94A3B8',
    'border':       'rgba(139, 92, 246, 0.3)',
    'border_hover': 'rgba(139, 92, 246, 0.6)',
}


class EyeOverlay(QWidget):
    """Transparent overlay that animates the opening of the eyelids via a clip rectangle."""
    def __init__(self, idle_path, active_path, parent=None):
        super().__init__(parent)
        self._glow = 0.0
        self._openness = 0.0 # 0.0 = closed (a thin slit), 1.0 = fully open
        self.idle_pixmap = QPixmap(idle_path) if os.path.exists(idle_path) else None
        self.active_pixmap = QPixmap(active_path) if os.path.exists(active_path) else None
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    @pyqtProperty(float)
    def glow(self):
        return self._glow
        
    @glow.setter
    def glow(self, value):
        self._glow = value
        self.update()

    @pyqtProperty(float)
    def openness(self):
        return self._openness
        
    @openness.setter
    def openness(self, value):
        self._openness = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        h = float(self.height())
        w = float(self.width())
        
        # 1. Always draw the closed eye image at full size (base layer)
        if self.idle_pixmap:
            # Fade out the closed eye as the open eye is revealed
            painter.setOpacity(1.0 - self._glow)
            painter.drawPixmap(self.rect(), self.idle_pixmap)
            
        # 2. Draw the open eye with an expanding clip mask tilted to match the closed eye angle
        if self.active_pixmap and self._openness > 0.0:
            from PyQt6.QtGui import QPainterPath, QTransform, QPolygonF
            from PyQt6.QtCore import QPointF
            
            # The closed eye strokes tilt at roughly -15 degrees
            angle = -15.0
            
            # Clip from a thin slit expanding to full height
            clip_h = 2.0 + (h - 2.0) * self._openness
            clip_y = (h - clip_h) / 2.0
            
            # Build a rectangle then rotate it around the center
            cx, cy = w / 2.0, h / 2.0
            # Make the rect wider than the widget to avoid clipping corners after rotation
            extra = w * 0.5
            rect_points = [
                QPointF(-extra, clip_y),
                QPointF(w + extra, clip_y),
                QPointF(w + extra, clip_y + clip_h),
                QPointF(-extra, clip_y + clip_h),
            ]
            
            # Rotate each point around the center
            transform = QTransform()
            transform.translate(cx, cy)
            transform.rotate(angle)
            transform.translate(-cx, -cy)
            
            rotated = [transform.map(p) for p in rect_points]
            
            clip_path = QPainterPath()
            clip_path.addPolygon(QPolygonF(rotated))
            clip_path.closeSubpath()
            
            painter.setClipPath(clip_path)
            painter.setOpacity(self._glow)
            painter.drawPixmap(self.rect(), self.active_pixmap)
            
        painter.end()


class FloatingWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Transparent, frameless window, always on top
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setGeometry(100, 100, 320, 500)
        
        self.old_pos = None
        self.expanded = False
        self._last_response = ""
        self._response_visible = False
        self._is_hovered = False
        
        self.setWindowOpacity(0.5)
        
        self.init_ui()
        
    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)
        self.setLayout(self.layout)
        
        # ── Main toggle button ──────────────────────────────────
        self.toggle_btn = QPushButton("")
        
        self.icon_idle_path = get_asset_path("icon_idle.png")
        self.icon_active_path = get_asset_path("icon_active.png")
        
        # Default to idle (transparent cornea) always
        if not os.path.exists(self.icon_idle_path):
            self.toggle_btn.setText("✦")
            
        self.toggle_btn.setFixedSize(40, 40)
        
        # Overlay handles all the customized drawing (opening eyelid effect + glow)
        self.eye_overlay = EyeOverlay(self.icon_idle_path, self.icon_active_path, self.toggle_btn)
        self.eye_overlay.setGeometry(6, 6, 28, 28)
        
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setFont(QFont("Inter", 14) if sys.platform != "win32" else QFont("Segoe UI", 14))
        self.set_inactive_style()
        
        # Glow shadow on toggle button
        self._toggle_shadow = QGraphicsDropShadowEffect()
        self._toggle_shadow.setBlurRadius(20) # Fixed so bounding box never changes
        self._toggle_shadow.setColor(QColor(0, 0, 0, 0)) # transparent by default
        self._toggle_shadow.setOffset(0, 0)
        self.toggle_btn.setGraphicsEffect(self._toggle_shadow)
        
        # Install event filter to handle dragging on the button itself
        self.toggle_btn.installEventFilter(self)
        self.is_dragging = False
        self.drag_start_pos = None
        
        # ── Menu container ──────────────────────────────────────
        self.menu_container = QWidget()
        self.menu_layout = QVBoxLayout()
        self.menu_layout.setContentsMargins(0, 0, 0, 0)
        self.menu_layout.setSpacing(6)
        self.menu_container.setLayout(self.menu_layout)
        
        menu_btn_style = f"""
            QPushButton {{
                background-color: {COLORS['surface']};
                color: {COLORS['text']};
                border-radius: 12px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 13px;
                border: 1px solid {COLORS['border']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_light']};
                border: 1px solid {COLORS['border_hover']};
            }}
        """
        
        self.explain_btn = QPushButton("🔍  Smart Explain")
        self.translate_btn = QPushButton("🌐  Translate")
        self.hide_app_btn = QPushButton("✕  Hide Widget")
        
        self.explain_btn.setStyleSheet(menu_btn_style)
        self.translate_btn.setStyleSheet(menu_btn_style)
        
        # Hide button gets a more subtle style
        hide_btn_style = menu_btn_style.replace(COLORS['surface'], COLORS['surface_light'])
        self.hide_app_btn.setStyleSheet(hide_btn_style)
        
        self.explain_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.translate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hide_app_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.explain_btn.clicked.connect(self.on_explain_clicked)
        self.translate_btn.clicked.connect(self.on_translate_clicked)
        self.hide_app_btn.clicked.connect(self.on_hide_app_clicked)
        
        self.menu_layout.addWidget(self.explain_btn)
        self.menu_layout.addWidget(self.translate_btn)
        self.menu_layout.addWidget(self.hide_app_btn)
        
        self.menu_container.hide()
        
        # ── Status label (pill style) ───────────────────────────
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text']};
                font-weight: bold;
                font-size: 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['primary_end']});
                border-radius: 10px;
                padding: 6px 14px;
            }}
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.hide()

        # ── Response text panel ─────────────────────────────────
        self.response_panel = QTextEdit()
        self.response_panel.setReadOnly(True)
        self.response_panel.setMaximumHeight(200)
        self.response_panel.setMinimumHeight(80)
        self.response_panel.setFont(QFont("Inter", 11) if sys.platform != "win32" else QFont("Segoe UI", 11))
        self.response_panel.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['surface']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                padding: 10px;
                selection-background-color: {COLORS['primary']};
            }}
            QScrollBar:vertical {{
                background: rgba(30, 30, 40, 100);
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['primary']};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        self.response_panel.hide()

        # ── Follow-up chat container ────────────────────────────
        self.chat_container = QWidget()
        self.chat_layout = QHBoxLayout()
        self.chat_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_layout.setSpacing(4)
        self.chat_container.setLayout(self.chat_layout)
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask a follow-up...")
        self.chat_input.setFont(QFont("Inter", 11) if sys.platform != "win32" else QFont("Segoe UI", 11))
        self.chat_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['surface']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 7px 10px;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS['primary']};
            }}
        """)
        
        self.send_btn = QPushButton("➤")
        self.send_btn.setFixedSize(34, 34)
        self.send_btn.setFont(QFont("Segoe UI", 13))
        self.send_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS['accent']}, stop:1 {COLORS['accent_dark']});
                color: white;
                border-radius: 8px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                background: {COLORS['accent']};
            }}
        """)
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.stop_audio_btn = QPushButton("⏹")
        self.stop_audio_btn.setFixedSize(34, 34)
        self.stop_audio_btn.setFont(QFont("Segoe UI", 12))
        self.stop_audio_btn.setToolTip("Stop speech")
        self.stop_audio_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['danger']};
                color: white;
                border-radius: 8px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {COLORS['danger_dark']};
            }}
        """)
        self.stop_audio_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Text panel toggle button
        self.text_toggle_btn = QPushButton("📄")
        self.text_toggle_btn.setFixedSize(34, 34)
        self.text_toggle_btn.setFont(QFont("Segoe UI", 13))
        self.text_toggle_btn.setToolTip("Show/hide response text")
        self.text_toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface']};
                color: {COLORS['text']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_light']};
                border: 1px solid {COLORS['border_hover']};
            }}
        """)
        self.text_toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(34, 34)
        self.close_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['danger']};
                color: white;
                border-radius: 8px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {COLORS['danger_dark']};
            }}
        """)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.chat_layout.addWidget(self.chat_input)
        self.chat_layout.addWidget(self.send_btn)
        self.chat_layout.addWidget(self.stop_audio_btn)
        self.chat_layout.addWidget(self.text_toggle_btn)
        self.chat_layout.addWidget(self.close_btn)
        
        self.chat_container.hide()
        
        # ── Connect signals ─────────────────────────────────────
        self.send_btn.clicked.connect(self.on_send_clicked)
        self.chat_input.returnPressed.connect(self.on_send_clicked)
        self.close_btn.clicked.connect(self.on_close_clicked)
        self.text_toggle_btn.clicked.connect(self.on_text_toggle_clicked)
        self.stop_audio_btn.clicked.connect(self.on_stop_audio_clicked)

        # ── Layout assembly ─────────────────────────────────────
        self.layout.addWidget(self.toggle_btn, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.menu_container, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.response_panel)
        self.layout.addWidget(self.chat_container)
        self.layout.addStretch()

    # ── Styles ──────────────────────────────────────────────────
    def set_inactive_style(self):
        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                border-radius: 20px;
                background: rgba(72, 2, 135, 230);
                color: rgba(255, 255, 255, 160);
                font-weight: bold;
                font-size: 14px;
                border: 1px solid rgba(100, 20, 180, 120);
            }}
            QPushButton:hover {{
                background: rgba(72, 2, 135, 255);
                color: white;
                border: 1px solid rgba(100, 20, 180, 200);
            }}
        """)
    def set_active_style(self):
        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                border-radius: 20px;
                background: rgba(72, 2, 135, 255);
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: 1px solid rgba(100, 20, 180, 200);
            }}
        """)

    def toggle_menu(self):
        self.expanded = not self.expanded
        self.menu_container.setVisible(self.expanded)
        if self.expanded:
            self.set_active_style()
        else:
            self.set_inactive_style()
        self.update_opacity()

    # ── Event filter for drag on toggle button ──────────────────
    def eventFilter(self, obj, event):
        if obj == self.toggle_btn:
            if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                self.is_dragging = False
                self.drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                return False 
                
            elif event.type() == QEvent.Type.MouseMove:
                if self.drag_start_pos is not None:
                    current_global_pos = event.globalPosition().toPoint()
                    diff = current_global_pos - self.drag_start_pos - self.frameGeometry().topLeft()
                    
                    if diff.manhattanLength() > 3 or self.is_dragging:
                        self.is_dragging = True
                        self.move(current_global_pos - self.drag_start_pos)
                        return True
                        
            elif event.type() == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
                if self.is_dragging:
                    self.is_dragging = False
                    self.drag_start_pos = None
                    return True
                else:
                    self.drag_start_pos = None
                    self.toggle_menu()
                    return True
                    
            elif event.type() == QEvent.Type.Enter:
                self._is_hovered = True
                self.update_opacity()
                return False
                
            elif event.type() == QEvent.Type.Leave:
                self._is_hovered = False
                self.update_opacity()
                return False
                    
        return super().eventFilter(obj, event)

    def update_opacity(self):
        is_active = self.expanded or self._response_visible or self._is_hovered
        target = 1.0 if is_active else 0.5
        
        if not hasattr(self, '_opacity_anim'):
            self._opacity_anim = QPropertyAnimation(self, b"windowOpacity")
            self._opacity_anim.setDuration(400)
            
        self._opacity_anim.stop()
        self._opacity_anim.setEndValue(target)
        self._opacity_anim.start()
        
        self.animate_glow()

    def animate_glow(self):
        """Animates the toggle button's shadow and cornea into a neon blue aura."""
        if not hasattr(self, '_glow_color_anim'):
            self._glow_color_anim = QPropertyAnimation(self._toggle_shadow, b"color")
            self._glow_color_anim.setDuration(800)
            
            # Animate the dynamic clipping eyelid
            self._eye_openness_anim = QPropertyAnimation(self.eye_overlay, b"openness")
            self._eye_openness_anim.setDuration(800)
            
            # Animate the inner eye color glow
            self._eye_glow_anim = QPropertyAnimation(self.eye_overlay, b"glow")
            self._eye_glow_anim.setDuration(800)
            
        self._glow_color_anim.stop()
        self._eye_openness_anim.stop()
        self._eye_glow_anim.stop()
        
        is_active = self.expanded or self._response_visible or self._is_hovered
        if is_active:
            # Glowy neon blue aura, open the eyelids, and fade in the blue pupil
            self._glow_color_anim.setEndValue(QColor(0, 240, 255, 255))
            self._eye_openness_anim.setEndValue(1.0)
            self._eye_glow_anim.setEndValue(1.0)
        else:
            # Drop shadow, close eyelids to a slit, fade out the blue pupil
            self._glow_color_anim.setEndValue(QColor(0, 0, 0, 0))
            self._eye_openness_anim.setEndValue(0.0)
            self._eye_glow_anim.setEndValue(0.0)
            
        self._glow_color_anim.start()
        self._eye_openness_anim.start()
        self._eye_glow_anim.start()

    # ── Standard drag on blank space ────────────────────────────
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
            
    # ── Status ──────────────────────────────────────────────────
    def show_status(self, text, fade=False):
        self.status_label.setText(text)
        
        if not hasattr(self, '_status_opacity'):
            from PyQt6.QtWidgets import QGraphicsOpacityEffect
            self._status_opacity = QGraphicsOpacityEffect(self.status_label)
            self.status_label.setGraphicsEffect(self._status_opacity)
            
        self._status_opacity.setOpacity(1.0)
        self.status_label.show()
        
        if hasattr(self, '_status_timer'):
            self._status_timer.stop()
            
        if fade:
            # Setup fade animation
            if not hasattr(self, '_fade_anim'):
                self._fade_anim = QPropertyAnimation(self._status_opacity, b"opacity")
                self._fade_anim.setDuration(2000) # 2 seconds fade
                self._fade_anim.setStartValue(1.0)
                self._fade_anim.setEndValue(0.0)
                self._fade_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
                self._fade_anim.finished.connect(self.status_label.hide)
            
            # Start fade after a delay
            self._status_timer = QTimer()
            self._status_timer.setSingleShot(True)
            self._status_timer.timeout.connect(self._fade_anim.start)
            self._status_timer.start(1000) # stay visible for 1s, then fade for 2s
        else:
            if hasattr(self, '_fade_anim') and self._fade_anim.state() == QPropertyAnimation.State.Running:
                self._fade_anim.stop()
                
            self._status_timer = QTimer()
            self._status_timer.setSingleShot(True)
            self._status_timer.timeout.connect(self.status_label.hide)
            self._status_timer.start(4000)

    # ── Response panel ──────────────────────────────────────────
    def update_response_panel(self, text):
        """Store and optionally display the latest response text."""
        self._last_response = text
        self.response_panel.setPlainText(text)
        # Auto-show the panel when a new response arrives
        if not self._response_visible:
            self._response_visible = True
            self.response_panel.show()
            self.update_opacity()

    def on_text_toggle_clicked(self):
        """Toggle visibility of the response text panel."""
        self._response_visible = not self._response_visible
        self.response_panel.setVisible(self._response_visible)

    def on_stop_audio_clicked(self):
        """Stop TTS speech mid-way."""
        tts_service.stop_speaking()
        self.show_status("⏹ Speech stopped", fade=True)
        
    def on_hide_app_clicked(self):
        """Hide the entire widget (requires system tray to bring back)."""
        self.expanded = False
        self.menu_container.hide()
        self.set_inactive_style()
        self.hide()

    # ── Action handlers ─────────────────────────────────────────
    def on_explain_clicked(self):
        self.show_status("⏳ Extracting...")
        QApplication.processEvents()
        self.hide()
        text = text_extractor.extract_text()
        self.show()
        
        if not text:
            self.show_status("⚠ Please select a text first!", fade=True)
            self.menu_container.hide()
            self.expanded = False
            self.set_inactive_style()
            return
            
        self.show_status("🔎 Detecting...")
        QApplication.processEvents()
        
        response, mode_info = llm_service.smart_explain(text)
        
        self.show_status("🔊 Speaking...")
        QApplication.processEvents()
        
        self.update_response_panel(response)
        tts_service.speak(response)
        self.show_status("✅ Done")
        self.chat_container.show()
        self.menu_container.hide()
        self.expanded = False
        self.set_active_style()

    def on_translate_clicked(self):
        self.show_status("⏳ Extracting...")
        QApplication.processEvents()
        self.hide()
        text = text_extractor.extract_text()
        self.show()
        
        if not text:
            self.show_status("⚠ Please select a text first!", fade=True)
            self.menu_container.hide()
            self.expanded = False
            self.set_inactive_style()
            return
            
        self.show_status("🌐 Translating...")
        QApplication.processEvents()
        
        response = llm_service.translate_and_explain(text)
        
        self.show_status("🔊 Speaking...")
        QApplication.processEvents()
        
        self.update_response_panel(response)
        tts_service.speak(response)
        self.show_status("✅ Done")
        self.chat_container.show()
        self.menu_container.hide()
        self.expanded = False
        self.set_active_style()
        self.update_opacity() # Call update_opacity on menu toggle
        
    def on_close_clicked(self):
        tts_service.stop_speaking()
        self.chat_container.hide()
        self.response_panel.hide()
        self._response_visible = False
        self.update_opacity()
        self._last_response = ""
        llm_service.clear_history()
        self.status_label.hide()
        self.set_inactive_style()
        
    def on_send_clicked(self):
        question = self.chat_input.text().strip()
        if not question:
            return
            
        self.chat_input.clear()
        
        self.show_status("💭 Thinking...")
        QApplication.processEvents()
        
        response = llm_service.ask_follow_up(question)
        
        self.show_status("🔊 Speaking...")
        QApplication.processEvents()
        
        self.update_response_panel(response)
        tts_service.speak(response)
        self.show_status("✅ Done")
