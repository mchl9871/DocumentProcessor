import ollama

def generate_summary(text, summary_type="full"):
    """Generate a summary using Ollama's local AI model."""
    if not text.strip():
        return "No text to summarize."

    truncated_text = text[:5000]

    if summary_type == "concise":
        prompt = f"""Summarize the following text in a concise manner in the third person, capturing only the key details and main points. Avoid rewriting the text from the first-person perspective. Do not include any introduction or phrases like "Here is a summary"; only provide the final summary text:{truncated_text}"""
    else:
        prompt = f"Summarize the following text in detail:\n\n{truncated_text}"

    try:
        # Use ollama.chat(...) instead of ollama.run(...)
        response = ollama.chat(
            model="llama3", 
            messages=[{"role": "user", "content": prompt}]
        )
        # 'response' should be a dict with a "message" key
        return response["message"]["content"].strip()
    except Exception as e:
        return f"Error summarizing text: {str(e)}"