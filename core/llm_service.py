import ollama
import json
import re

# Model assignments
MODEL_EXPLAIN = 'llama3:8b'     # Plain English explanations
MODEL_DETECT = 'qwen2.5:7b'    # Language/idiom detection, translation, idiom explanation

# Global conversation history for follow-ups
conversation_history = []
_last_model = MODEL_EXPLAIN  # Track which model was used last for follow-ups


def clear_history():
    global conversation_history
    conversation_history.clear()


def detect_language_and_idioms(text):
    """
    Uses qwen2.5:7b to detect the language of the text and whether it contains idioms.
    Returns (language: str, has_idioms: bool).
    """
    prompt = f"""Analyze the following text. Respond ONLY with a JSON object, no other text.
The JSON must have exactly two keys:
- "language": the language the text is written in (e.g. "English", "Spanish", "French")
- "has_idioms": true if the text contains idioms, proverbs, or figurative expressions, false otherwise

Text:
\"{text}\""""

    try:
        response = ollama.chat(model=MODEL_DETECT, messages=[
            {'role': 'user', 'content': prompt}
        ])
        raw = response.message.content.strip()

        # Try to extract JSON from the response
        # Look for JSON pattern in the response
        json_match = re.search(r'\{.*?\}', raw, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            language = data.get('language', 'Unknown')
            has_idioms = bool(data.get('has_idioms', False))
            return language, has_idioms

        # Fallback: assume English, no idioms
        return 'English', False

    except Exception:
        # On any error, fall back to English/no idioms so explain still works
        return 'English', False


def explain_text(text):
    """Explain English text using Llama 3."""
    global conversation_history, _last_model

    prompt = f"""You are a helpful teacher. Please explain the following text in simple English so that a student can easily understand. Provide easy-to-relate examples. Keep it concise but educational.
    
Text to explain:
\"{text}\""""

    clear_history()
    _last_model = MODEL_EXPLAIN

    msg = {'role': 'user', 'content': prompt}
    conversation_history.append(msg)

    try:
        response = ollama.chat(model=MODEL_EXPLAIN, messages=conversation_history)
        response_text = response.message.content
        conversation_history.append({'role': 'assistant', 'content': response_text})
        return response_text
    except Exception as e:
        return f"Error communicating with Ollama: {str(e)}"


def translate_and_explain(text):
    """Translate non-English text or explain idioms using Qwen 2.5:7b."""
    global conversation_history, _last_model

    prompt = f"""You are a helpful translation assistant. For the following text:
1. Detect the language it is written in.
2. Translate it into English.
3. Explain the meaning, especially focusing on any regional idioms, proverbs, or cultural nuances.

Text:
\"{text}\""""

    clear_history()
    _last_model = MODEL_DETECT

    msg = {'role': 'user', 'content': prompt}
    conversation_history.append(msg)

    try:
        response = ollama.chat(model=MODEL_DETECT, messages=conversation_history)
        response_text = response.message.content
        conversation_history.append({'role': 'assistant', 'content': response_text})
        return response_text
    except Exception as e:
        return f"Error communicating with Ollama: {str(e)}"


def explain_idiom(text):
    """Explain English idioms/figurative expressions using Qwen 2.5:7b."""
    global conversation_history, _last_model

    prompt = f"""You are a language expert. The following English text contains idioms, proverbs, or figurative expressions.
1. Identify each idiom or figurative expression in the text.
2. Explain the literal vs figurative meaning of each one.
3. Give a simple overall explanation of what the text means.

Text:
\"{text}\""""

    clear_history()
    _last_model = MODEL_DETECT

    msg = {'role': 'user', 'content': prompt}
    conversation_history.append(msg)

    try:
        response = ollama.chat(model=MODEL_DETECT, messages=conversation_history)
        response_text = response.message.content
        conversation_history.append({'role': 'assistant', 'content': response_text})
        return response_text
    except Exception as e:
        return f"Error communicating with Ollama: {str(e)}"


def smart_explain(text):
    """
    Smart routing entry point:
    - Detects language and idiom presence using qwen2.5:7b
    - English + no idioms  →  llama3 (explain_text)
    - English + idioms     →  qwen2.5:7b (explain_idiom)
    - Non-English          →  qwen2.5:7b (translate_and_explain)

    Returns (response_text, mode_description).
    """
    language, has_idioms = detect_language_and_idioms(text)

    is_english = language.lower().strip() in ('english', 'en')

    if is_english and not has_idioms:
        response = explain_text(text)
        return response, f"Explained with Llama 3 (English, no idioms)"
    elif is_english and has_idioms:
        response = explain_idiom(text)
        return response, f"Idiom detected — explained with Qwen 2.5:7b"
    else:
        response = translate_and_explain(text)
        return response, f"Detected {language} — translated with Qwen 2.5:7b"


def ask_follow_up(question):
    """Continue the conversation using whichever model was last used."""
    global conversation_history, _last_model

    msg = {'role': 'user', 'content': question}
    conversation_history.append(msg)

    try:
        response = ollama.chat(model=_last_model, messages=conversation_history)
        response_text = response.message.content
        conversation_history.append({'role': 'assistant', 'content': response_text})
        return response_text
    except Exception as e:
        return f"Error communicating with Ollama: {str(e)}"
