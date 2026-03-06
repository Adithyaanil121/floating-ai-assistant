# Floating AI Assistant Architecture

This document describes the module structure and design of the Floating AI Assistant.

## Project Structure
```text
floating-ai-assistant
│
├── README.md
├── requirements.txt
├── main.py
│
├── core
│   ├── llm_service.py     # Handles interaction with the Local LLM models (Ollama)
│   ├── text_extractor.py  # Handles extraction of text from the screen using OCR or Clipboard
│   └── tts_service.py     # Provides Text-to-Speech capabilities
│
├── ui
│   └── floating_widget.py # Contains the PyQt6 logic for the transparent, Draggable UI
│
├── assets
│   ├── demo.gif
│   └── screenshot.png
│
└── docs
    └── architecture.md
```

## Core Components
- **UI Layer**: Built with PyQt6, providing a frameless, transparent widget that stays always on top.
- **Service Layer**: Decoupled modules (`core/`) that abstract the logic for text extraction, LLM interactions, and Audio playback.
