# Floating AI Assistant

![Demo](assets/demo.gif)

A Python-based desktop widget that floats above your other windows, allowing you to quickly extract text from any application on your screen, have it explained or translated by a local Large Language Model (LLM), and read aloud to you using Text-to-Speech (TTS).

## Features

![Screenshot](assets/screenshot.png)

- **Always-on-top Floating Widget**: A non-intrusive, Mobizen-like floating button ("M") that stays on top of other windows. You can drag it anywhere on your screen.
- **Screen Text Extraction**: Quickly copies selected text from any active window using automated keyboard shortcuts (`Ctrl+C`).
- **Explain Text**: AI explains complex text in simple English.
- **Translate Text**: AI detects the language of the selected text, translates it into English, and explains any regional idioms or cultural nuances.
- **Local AI Processing**: Uses [Ollama](https://ollama.com/) to process text completely locally for privacy and speed. Defaults to the `llama3.2:3b` model.
- **Text-to-Speech (TTS)**: Reads out the AI's response using your system's default text-to-speech engine.
- **Follow-up Chat**: Features a built-in chat interface, allowing you to ask follow-up questions to the AI about the extracted text.

## Prerequisites

To run this application, you must have the following installed on your system:
- **Python 3.x**
- **Ollama**: Download and install from [ollama.com](https://ollama.com/).

## Installation

1. Clone or download this project to your local machine.
2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Pull the required language model through Ollama (this is a one-time setup):
   ```bash
   ollama pull llama3.2:3b
   ```
   *(You can change the `MODEL` variable in `llm_service.py` if you prefer to use a different local model).*

## Usage

1. Start the application by running:
   ```bash
   python main.py
   ```
2. A floating button with an "M" will appear on your screen. You can drag it to any convenient location.
3. Highlight/select some text in any application (e.g., a PDF, a web browser, or a document).
4. Click the floating "M" button to open the menu options:
   - **Start Explain**: Copies the text, explains it simply, and reads the explanation aloud.
   - **Start Translation**: Copies the text, translates it to English, explains context, and reads it aloud.
5. After the AI responds, a chat input box will appear. You can type follow-up questions directly into the widget.
6. Click the close ("X") button on the widget to hide the chat history and collapse the menu back to the single floating button.

## Project Structure

- `main.py`: The entry point and PyQT6 user interface containing the runner.
- `ui/floating_widget.py`: The PyQT6 user interface containing the `FloatingWidget` class.
- `core/llm_service.py`: Handles communication with the local Ollama instance, managing prompts, and conversation history.
- `core/text_extractor.py`: Manages the automated text extraction by simulating `Ctrl+C` and reading the clipboard using `pyautogui` and `pyperclip`.
- `core/tts_service.py`: Provides the asynchronous text-to-speech functionality using `pyttsx3`.
