import os
import sys
import requests
from dotenv import load_dotenv
from google import genai


OLLAMA_MODELS = {
    "llama3.1": "llama3.1",
    "llama3.1:latest": "llama3.1",
    "phi3": "phi3",
    "phi3:latest": "phi3",
    "deepseek-r1:1.5b": "deepseek-r1:1.5b",
}

GEMINI_MODELS = {
    "gemini-2.5-flash": "gemini-2.5-flash",
    "gemini-2.5-flash-lite": "gemini-2.5-flash-lite",
    "gemini-3-flash-preview": "gemini-3-flash-preview",
}


def call_ollama(model: str, prompt: str) -> str:
    """Call local Ollama model."""
    try:
        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )

        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response returned from Ollama.")

    except requests.exceptions.ConnectionError:
        return "[Ollama Error] Ollama is not running. Please open Ollama and try again."

    except requests.exceptions.Timeout:
        return "[Ollama Error] Request timed out. The model may still be loading."

    except Exception as error:
        return f"[Ollama Error] {error}"


def call_gemini(model: str, prompt: str) -> str:
    """Call Google Gemini model."""
    try:
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            return "[Gemini Error] GOOGLE_API_KEY not found. Please check your .env file."

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )

        return response.text if response.text else "No response returned from Gemini."

    except Exception as error:
        return f"[Gemini Error] {error}"


def prompt_model(model: str, prompt: str) -> str:
    """
    Select the correct provider based on the model name
    and return the model response.
    """
    model = model.strip().lower()

    if model in OLLAMA_MODELS:
        selected_model = OLLAMA_MODELS[model]
        return call_ollama(selected_model, prompt)

    elif model in GEMINI_MODELS:
        selected_model = GEMINI_MODELS[model]
        return call_gemini(selected_model, prompt)

    else:
        return (
            "[Model Error] Unsupported model.\n"
            "Available models:\n"
            "- llama3.1\n"
            "- phi3\n"
            "- deepseek-r1:1.5b\n"
            "- gemini-2.5-flash\n"
            "- gemini-2.5-flash-lite\n"
            "- gemini-3-flash-preview"
        )


def main():
    if len(sys.argv) >= 3:
        model = sys.argv[1]
        prompt = " ".join(sys.argv[2:])
    else:
        model = "llama3.1"
        prompt = "Tell me one Malaysian joke"

    print("\n--- RESPONSE ---\n")
    result = prompt_model(model, prompt)
    print(result)


if __name__ == "__main__":
    main()