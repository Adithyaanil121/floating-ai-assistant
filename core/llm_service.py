import ollama

# We use a fast, common model like llama3 or mistral. 
# You should ensure the user has pulled at least one. We'll use the local model.
MODEL = 'llama3.2:3b'

# Global conversation history for follow-ups
conversation_history = []

def clear_history():
    global conversation_history
    conversation_history.clear()

def explain_text(text):
    prompt = f"""You are a helpful assistant. Please explain the following text in simple English. Keep it concise but informative.
    
Text to explain:
\"{text}\""""
    
    global conversation_history
    clear_history()
    
    msg = {'role': 'user', 'content': prompt}
    conversation_history.append(msg)
    
    try:
        response = ollama.chat(model=MODEL, messages=conversation_history)
        response_text = response.message.content
        conversation_history.append({'role': 'assistant', 'content': response_text})
        return response_text
    except Exception as e:
        return f"Error communicating with Ollama: {str(e)}"

def translate_and_explain(text):
    prompt = f"""You are a helpful translation assistant. For the following text:
1. Detect the language it is written in.
2. Translate it into English.
3. Explain the meaning, especially focusing on any regional idioms, proverbs, or cultural nuances.

Text:
\"{text}\""""
    
    global conversation_history
    clear_history()
    
    msg = {'role': 'user', 'content': prompt}
    conversation_history.append(msg)
    
    try:
        response = ollama.chat(model=MODEL, messages=conversation_history)
        response_text = response.message.content
        conversation_history.append({'role': 'assistant', 'content': response_text})
        return response_text
    except Exception as e:
        return f"Error communicating with Ollama: {str(e)}"

def ask_follow_up(question):
    global conversation_history
    msg = {'role': 'user', 'content': question}
    conversation_history.append(msg)
    
    try:
        response = ollama.chat(model=MODEL, messages=conversation_history)
        response_text = response.message.content
        conversation_history.append({'role': 'assistant', 'content': response_text})
        return response_text
    except Exception as e:
        return f"Error communicating with Ollama: {str(e)}"
