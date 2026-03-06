import os
import shutil

os.makedirs('core', exist_ok=True)
os.makedirs('ui', exist_ok=True)
os.makedirs('assets', exist_ok=True)
os.makedirs('docs', exist_ok=True)

with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

floating_widget_lines = []
floating_widget_lines.append('from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QApplication\n')
floating_widget_lines.append('from PyQt6.QtCore import Qt, QTimer, QEvent\n')
floating_widget_lines.append('from core import llm_service\n')
floating_widget_lines.append('from core import text_extractor\n')
floating_widget_lines.append('from core import tts_service\n\n')

floating_widget_lines.extend(lines[9:284])

with open('ui/floating_widget.py', 'w', encoding='utf-8') as f:
    f.writelines(floating_widget_lines)

main_lines = []
main_lines.append('import sys\n')
main_lines.append('import ctypes\n')
main_lines.append('from PyQt6.QtWidgets import QApplication\n')
main_lines.append('from PyQt6.QtCore import Qt\n')
main_lines.append('from ui.floating_widget import FloatingWidget\n\n')
main_lines.extend(lines[284:])

with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(main_lines)

os.system("git mv llm_service.py core/")
os.system("git mv text_extractor.py core/")
os.system("git mv tts_service.py core/")
os.system("git add core/ ui/ assets/ docs/ main.py")
print("Refactoring complete.")
