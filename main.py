import sys
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.floating_widget import FloatingWidget
import os
import sys

def get_asset_path(filename):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, 'assets', filename)

if __name__ == '__main__':
    # Fix for scaling on high DPI displays
    if hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Required to make PyAutoGUI hotkeys work across apps correctly on windows
    myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    
    # Crucial: Don't quit the entire app when the widget is hidden
    app.setQuitOnLastWindowClosed(False)
    
    ex = FloatingWidget()
    ex.show()
    
    # Set up the System Tray Icon
    from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
    from PyQt6.QtGui import QIcon, QPixmap, QColor
    
    icon_path = get_asset_path("icon.png")
    if os.path.exists(icon_path):
        tray_icon = QSystemTrayIcon(QIcon(icon_path), app)
    else:
        # Create a simple generic icon programmatically (since we don't have an .ico file)
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor("transparent"))
        from PyQt6.QtGui import QPainter
        painter = QPainter(pixmap)
        painter.setBrush(QColor(139, 92, 246)) # matches our primary purple
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 28, 28)
        painter.setPen(QColor("white"))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "M")
        painter.end()
        tray_icon = QSystemTrayIcon(QIcon(pixmap), app)
        
    tray_icon.setToolTip("Floating AI Assistant")
    
    # Tray menu
    tray_menu = QMenu()
    
    show_action = tray_menu.addAction("Show Widget")
    show_action.triggered.connect(ex.show)
    
    quit_action = tray_menu.addAction("Quit Application")
    quit_action.triggered.connect(app.quit)
    
    tray_icon.setContextMenu(tray_menu)
    
    # Also allow left-clicking the tray icon to show the widget
    def on_tray_activated(reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            ex.show()
            
    tray_icon.activated.connect(on_tray_activated)
    tray_icon.show()
    
    # For multiprocessing support on Windows (pyttsx3 in isolated processes)
    import multiprocessing
    multiprocessing.freeze_support()
    
    sys.exit(app.exec())
