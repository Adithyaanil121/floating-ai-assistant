import sys
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.floating_widget import FloatingWidget

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
    ex = FloatingWidget()
    ex.show()
    sys.exit(app.exec())
