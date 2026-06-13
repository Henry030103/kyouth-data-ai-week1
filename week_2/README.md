# Week 2 - LLM Model Prompting Setup

## Project Overview

This project demonstrates how to call both local and cloud-based large language models using Python. The local models are handled through Ollama, while the cloud models are handled through Google Gemini API. The main function accepts a model name and a prompt, then returns the generated text response.

## Project Structure

```text
week_2/
├── data/
├── prompt_model.py
├── rate_limits.txt
├── pyproject.toml
├── uv.lock
├── README.md
└── .env
```

The `.env` file is used to store the Google API key locally and is not committed to GitHub.

## Models Used

### Ollama Models

The following local Ollama models were installed and tested:

```text
llama3.1
phi3
deepseek-r1:1.5b
```

### Gemini Models

The following Google Gemini models were included:

```text
gemini-2.5-flash
gemini-2.5-flash-lite
gemini-3-flash-preview
```

## Rate Limits

The rate limits are stored in `rate_limits.txt` using the required format:

```text
gemini-2.5-flash 5 250K 20
gemini-2.5-flash-lite 10 250K 20
gemini-3-flash-preview 5 250K 20
```

The values represent:

```text
RPM = Requests Per Minute
TPM = Tokens Per Minute
RPD = Requests Per Day
```

## Environment Setup

The project was initialized using `uv`.

Required packages:

```text
requests
google-genai
python-dotenv
```

To install the dependencies, run:

```powershell
uv sync
```

## API Key Setup

Create a `.env` file inside the `week_2` folder and add the Google API key:

```env
GOOGLE_API_KEY=your_api_key_here
```

The `.env` file is ignored using `.gitignore` to prevent the API key from being uploaded to GitHub.

## How to Run

Run the program using:

```powershell
uv run python prompt_model.py <model_name> "<prompt>"
```

Example:

```powershell
uv run python prompt_model.py llama3.1 "tell me one Malaysian joke"
```

Another example:

```powershell
uv run python prompt_model.py gemini-2.5-flash "tell me one Malaysian joke"
```

## Error Handling

The program includes error handling for common issues such as:

```text
Ollama not running
Request timeout
Missing Google API key
Unsupported model name
Gemini API errors
```

Instead of crashing, the function returns a readable error message.

## Reflection

Through this task, I learned how to set up and use both local and cloud-based language models in a Python project. Ollama allows local model execution, which provides more control and privacy, while Google Gemini provides access to cloud-based models with rate limits. I also learned the importance of storing API keys securely using a `.env` file and excluding sensitive files from GitHub using `.gitignore`.
