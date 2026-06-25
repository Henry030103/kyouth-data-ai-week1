# K-Youth Data AI Project

## Project Overview

This repository contains the work completed for the K-Youth Data AI program. The project focuses on building a data processing and AI-assisted workflow for job data. It includes data extraction, transformation, model prompting, job skill tagging, and skill gap analysis.

The main goal of the project is to process job-related data and use it to identify technical skill requirements from job descriptions. The project also compares these required skills against a resume text file to determine possible skill gaps. The system is designed to be modular, with separate scripts for different responsibilities.

## Repository Structure

```text
K-YOUTH DATA PROGRAM/
├── week1/
│   ├── src/
│   ├── main.py
│   ├── pyproject.toml
│   ├── uv.lock
│   └── README.md
├── week_2/
│   ├── data/
│   │   ├── .gitkeep
│   │   └── resume.txt
│   ├── prompt_model.py
│   ├── tag_data.py
│   ├── find_skill_gaps.py
│   ├── rate_limits.txt
│   ├── pyproject.toml
│   ├── uv.lock
│   └── README.md
├── .gitignore
└── README.md
```

The `.env` file is used locally to store API keys and is intentionally excluded from GitHub. The `.venv` folders are also excluded because virtual environments should not be committed.

## Setup Instructions

### Prerequisites

Before running the project, make sure the following are installed:

```text
Python
uv
Git
Ollama
Google AI Studio API key
SQLite database viewer extension in VS Code
```

This project uses `uv` to manage dependencies and run Python scripts.

### Environment Setup

Navigate to the `week_2` folder:

```powershell
cd week_2
```

Create or activate the virtual environment:

```powershell
uv venv
.\.venv\Scripts\activate.ps1
```

Install dependencies:

```powershell
uv sync
```

If dependencies are missing, install them manually:

```powershell
uv add requests google-genai python-dotenv pydantic
```

### API Key Setup

Create a `.env` file inside the `week_2` folder:

```text
week_2/.env
```

Add the Google API key using this format:

```env
GOOGLE_API_KEY=your_api_key_here
```

The actual API key must not be committed to GitHub. The `.env` file is ignored using `.gitignore`.

### Ollama Setup

Install Ollama and verify that it is running:

```powershell
ollama -v
curl.exe 127.0.0.1:11434
```

Install the required Ollama models:

```powershell
ollama pull llama3.1
ollama pull phi3
ollama pull deepseek-r1:1.5b
```

Check installed models:

```powershell
ollama list
```

## Usage

### 1. Prompting Local and Gemini Models

The `prompt_model.py` script allows the user to call either local Ollama models or Gemini models.

Run the script using:

```powershell
uv run python prompt_model.py <model_name> "<prompt>"
```

Example using Ollama:

```powershell
uv run python prompt_model.py llama3.1 "tell me one Malaysian joke"
```

Example using Gemini:

```powershell
uv run python prompt_model.py gemini-2.5-flash "tell me one Malaysian joke"
```

Supported local models:

```text
llama3.1
phi3
deepseek-r1:1.5b
```

Supported Gemini models:

```text
gemini-2.5-flash
gemini-2.5-flash-lite
gemini-3-flash-preview
```

### 2. Job Data Tagging

The `tag_data.py` script reads the `jobs` table from the SQLite database and fills in empty `tech_stack` values based on the job descriptions.

Before running the script, place the SQLite database file here:

```text
week_2/data/jobs_d1.db
```

Run:

```powershell
uv run python tag_data.py
```

Expected output format:

```text
Analyzed Job 91397216: Python, SQL, Java
Analyzed Job 91347112: Java, Spring Framework, Spring Boot
Total tokens used: 1819, took 18718.824ms
```

The script uses batch processing and does not send the entire table in one prompt. It also handles errors gracefully and prints readable messages instead of crashing.

### 3. Skill Gap Analysis

The `find_skill_gaps.py` script reads a resume text file and compares it against the technical skills stored in the database.

Required files:

```text
week_2/data/resume.txt
week_2/data/jobs_d1.db
```

Run:

```powershell
uv run python find_skill_gaps.py
```

Expected output format:

```text
gaps=['docker', 'git', 'github actions', 'java', 'linux', 'mongodb', 'node.js', 'php', 'postgresql', 'power bi', 'spring boot', 'spring framework', 'sql'] time=5 tokens=340
input_tokens=272 output_tokens=68
top_demand_skills=['python: 4', 'mysql: 2', 'sql: 2', 'docker: 1', 'git: 1']
demand_difference=3
prompt_optimization={'baseline_tokens': 432, 'optimized_tokens': 240, 'token_reduction_percent': 44.44}
algorithm_optimization={'naive_time_ms': 2.942, 'optimized_time_ms': 0.375, 'time_reduction_percent': 87.24}
jailbreak_safety={'safe_to_process': True, 'detected_phrases': []}
```

The exact gap values may differ depending on the contents of `jobs_d1.db` and `resume.txt`.

## API / Function Reference

### `prompt_model(model: str, prompt: str) -> str`

Purpose:

```text
Calls a selected local Ollama model or Gemini model and returns a generated text response.
```

Inputs:

```text
model: model name, such as llama3.1 or gemini-2.5-flash
prompt: user prompt as a string
```

Output:

```text
A string response from the selected model, or a readable error message.
```

### `tag_data(db_url: str)`

Purpose:

```text
Reads the jobs table from a SQLite database and fills missing tech_stack values.
```

Inputs:

```text
db_url: path to the SQLite database file
```

Output:

```text
Updates the tech_stack column in the database and returns token/time related information.
```

Main processing steps:

```text
1. Read rows where tech_stack is empty.
2. Process rows in batches.
3. Send job descriptions to Gemini.
4. Parse the returned technical skills.
5. Update the database.
6. Print each updated job.
```

### `find_skill_gaps(input_file_path: str, db_url: str) -> SkillGapResult`

Purpose:

```text
Reads a resume text file and identifies technical skills that are required by job postings but missing from the resume.
```

Inputs:

```text
input_file_path: path to resume.txt
db_url: path to jobs_d1.db
```

Output:

```text
A Pydantic SkillGapResult object.
```

The `SkillGapResult` contains:

```text
gaps
time
tokens
input_tokens
output_tokens
skill_demand
top_demand_skills
demand_difference
prompt_optimization
algorithm_optimization
jailbreak_safety
```

## Data / Assumptions

The project uses a SQLite database containing a `jobs` table. The important columns used are:

```text
source_id
job_title
company
description
tech_stack
```

The `tech_stack` column is filled by `tag_data.py` based on the job description.

The skill gap analysis assumes that:

```text
1. The resume is provided as plain text in resume.txt.
2. The database contains a jobs table with a tech_stack column.
3. Skills are separated by commas in the tech_stack field.
4. Skills are converted to lowercase for consistent comparison.
5. Skills separated by "/" are treated as separate skills, except A/B testing and CI/CD.
6. Non-technical skills such as leadership and management are ignored where possible.
7. Certifications can be ignored even if they are tech-related.
```

The data flow is:

```text
Job descriptions
→ tag_data.py
→ tech_stack column in jobs_d1.db
→ find_skill_gaps.py
→ missing skills from resume
```

## Testing

The system was tested by running each script from the terminal.

### Model Prompting Test

Commands used:

```powershell
uv run python prompt_model.py llama3.1 "tell me one Malaysian joke"
uv run python prompt_model.py phi3 "tell me one Malaysian joke"
uv run python prompt_model.py deepseek-r1:1.5b "tell me one Malaysian joke"
uv run python prompt_model.py gemini-2.5-flash "tell me one Malaysian joke"
uv run python prompt_model.py gemini-2.5-flash-lite "tell me one Malaysian joke"
uv run python prompt_model.py gemini-3-flash-preview "tell me one Malaysian joke"
```

The expected result is that each command prints a response under the response section without crashing.

### Data Tagging Test

Command used:

```powershell
uv run python tag_data.py
```

The database was checked before and after running the script to confirm that the `tech_stack` column changed from empty or NULL values into generated technical skills.

### Skill Gap Test

Command used:

```powershell
uv run python find_skill_gaps.py
```

The output was checked to ensure that:

```text
1. gaps are returned as a list.
2. skills are lowercase.
3. results are sorted.
4. time and token values are returned.
5. bonus statistics are printed.
6. no stack trace appears during normal execution.
```

The skill gap logic is deterministic because it uses regular expression matching instead of relying on random LLM output.

## Limitations

The system has several limitations.

First, the quality of the skill gap result depends on the quality of the `tech_stack` values generated earlier. If `tag_data.py` produces incomplete or overly general skills, the skill gap output will also be limited.

Second, the tagging process may produce slight inaccuracies because it uses a language model to infer technical skills from job descriptions. This is acceptable for the task, but it may not be fully reliable for production use.

Third, token counts are estimated using a simple rule when exact token usage is unavailable. This means the token numbers may not perfectly match the model provider's internal counting.

Fourth, the skill gap analysis uses direct matching and regular expressions. It may not detect related skills or synonyms. For example, it may treat `power bi` and `business intelligence dashboarding` as different concepts.

Fifth, MCP integration was not implemented. The project uses direct SQLite access for database operations.

## Architecture Reflection

The system was designed using a modular structure so that each file has a clear responsibility. The `prompt_model.py` file focuses on model prompting, `tag_data.py` focuses on database tagging, and `find_skill_gaps.py` focuses on resume comparison and skill gap analysis. This separation makes the project easier to understand, test, and maintain.

A key design choice was to use batch processing in `tag_data.py` instead of sending the entire database table in one prompt. This reduces the risk of exceeding token limits and makes the program more stable when working with API rate limits. The rate limit values are stored separately in `rate_limits.txt`, which keeps configuration separate from the main logic.

For skill gap analysis, deterministic regex-based matching was used instead of relying fully on an LLM. This decision was made because determinism is important for Day 3–4, where repeated runs should produce the same result. This improves reliability and makes the output easier to verify.

There are some trade-offs in the design. The system prioritizes simplicity and reliability over advanced semantic understanding. For example, direct regex matching is fast and deterministic, but it may miss related skills or synonyms. Similarly, storing API keys in `.env` improves security, but users must configure their environment correctly before running the program.

If given more time, I would improve the project by adding MCP integration, better skill normalization, synonym mapping, and stronger validation of model-generated outputs. I would also improve the tagging quality by comparing outputs across multiple runs and adding a more advanced evaluation method for technical skill extraction.

--------------------

# K-Youth Data Program - Week 3 Full-Stack Chat Application

## Project Overview

This Week 3 project builds and containerizes a full-stack chat application with a separated frontend and backend architecture. The main goal of the project is to create a web-based chatbot interface that allows users to enter a message, upload a PDF document, extract the PDF text, and send the combined information to a backend service for processing.

The frontend is built using FastAPI, Jinja templates, Bootstrap CSS, and JavaScript. It provides a chat interface with a scrollable chat history, a user input box, a send button, and a PDF upload feature. When a user uploads a PDF, the frontend extracts the text from the PDF and prepares it together with the user message as JSON data.

The backend is built using FastAPI. It exposes a `POST /chat` endpoint that receives JSON data from the frontend, including the user message, extracted PDF text, and uploaded file name. The backend then calls the previous Week 2 module, specifically the skill-gap analysis logic, and returns the output as a JSON response.

The project follows a microservices-style architecture where the frontend and backend are separated into different services. Each service has its own Dockerfile, and both services are managed together using Docker Compose. Docker Compose allows the frontend and backend containers to run together on the same Docker network, making communication between the services more organized and reproducible.

---

### Setup Instructions

#### Prerequisites

Before running the project, make sure the following tools are installed:

* Python
* uv
* Docker Desktop
* Docker Compose
* Windows Subsystem for Linux 2, if using Docker Desktop on Windows

Docker Desktop must be running before using Docker or Docker Compose commands. On Windows, WSL 2 should be installed and enabled because Docker Desktop depends on it for Linux container support.

If the Week 2 module uses a local LLM service such as Ollama, make sure Ollama is running on the host machine and accessible at:

```text
http://localhost:11434
```

When running inside Docker, the backend can access the host machine through:

```text
http://host.docker.internal:11434
```

#### Project Structure

The Week 3 project is organized as follows:

```text
week_3/
├── frontend/
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── .python-version
│   ├── pyproject.toml
│   ├── uv.lock
│   └── src/
│       ├── main.py
│       └── templates/
│           └── chat_page.html
│
├── backend/
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── .python-version
│   ├── pyproject.toml
│   ├── uv.lock
│   └── src/
│       ├── app.py
│       └── week_2/
│           ├── data/
│           │   ├── jobs_d1.db
│           │   └── resume.txt
│           ├── find_skill_gaps.py
│           ├── prompt_model.py
│           ├── rate_limits.txt
│           └── tag_data.py
│
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

#### Environment Variables

The project uses environment variables so that service URLs are not hard-coded.

The example environment file is located at:

```text
week_3/.env.example
```

The main environment variable is:

```env
BACKEND_URL=http://backend:8001/chat
```

This value is used in Docker Compose so the frontend service can communicate with the backend service using the Docker Compose service name `backend`.

A local `.env` file can also be created inside the `week_3` folder for local development:

```env
BACKEND_URL=http://127.0.0.1:8001/chat
```

The `.env` file should not be committed to GitHub because it may contain environment-specific configuration or secrets.

#### Manual Dependency Installation

The frontend and backend dependencies were installed using `uv`.

Frontend dependencies:

```bash
cd week_3/frontend
uv add fastapi jinja2 uvicorn python-dotenv
```

Backend dependencies:

```bash
cd week_3/backend
uv add fastapi jinja2 uvicorn python-dotenv
```

---

### Usage

#### Running the Full Application with Docker Compose

The recommended way to run the full Week 3 project is through Docker Compose.

From the `week_3` folder, run:

```bash
cd week_3
docker compose up --build
```

This command builds and starts both services:

* Frontend service
* Backend service

After both services are running, open the frontend in a browser:

```text
http://localhost:8000
```

The backend health check can be accessed at:

```text
http://localhost:8001
```

The expected backend health check response is:

```json
{
  "status": "Backend is running"
}
```

#### Expected Inputs

The application accepts:

* A user message typed into the chat input box
* An optional PDF file upload

When a PDF is uploaded, the frontend extracts the text from the PDF and sends it together with the user message.

Example JSON payload:

```json
{
  "message": "Please analyse this resume",
  "pdf_text": "Extracted PDF text content...",
  "file_name": "resume.pdf"
}
```

#### Expected Outputs

The backend returns a JSON response containing the Week 2 analysis output.

Example response:

```json
{
  "reply": "gaps=['docker', 'git', 'python', 'sql']...",
  "user_message": "Please analyse this resume",
  "file_name": "resume.pdf"
}
```

The frontend displays the backend response inside the chat history.

A successful response may include information such as:

```text
gaps=['docker', 'git', 'github actions', 'linux', 'mongodb', 'mysql', 'node.js', 'php', 'postgresql', 'power bi', 'python', 'sql']
top_demand_skills=['python: 4', 'mysql: 2', 'sql: 2', 'docker: 1', 'git: 1']
prompt_optimization={...}
algorithm_optimization={...}
jailbreak_safety={...}
```

---

### API / Function Reference

#### Frontend Service

The frontend service is located in:

```text
week_3/frontend/src/main.py
```

The frontend is responsible for:

* Serving the chat page
* Rendering the Bootstrap-based user interface
* Maintaining the scrollable chat history
* Accepting user text input
* Accepting PDF uploads
* Extracting PDF text in the browser
* Sending JSON requests through the frontend `/chat` proxy route
* Forwarding requests to the backend service through the Docker network

Main frontend route:

| Method | Endpoint | Description                                          |
| ------ | -------- | ---------------------------------------------------- |
| `GET`  | `/`      | Displays the chatbot web page                        |
| `POST` | `/chat`  | Proxies the user message and PDF text to the backend |

The frontend proxy route is used so that the browser sends requests to the frontend service first. The frontend service then forwards the JSON request to the backend service using the Docker Compose service name:

```text
http://backend:8001/chat
```

This avoids relying on the browser to resolve Docker internal service names.

#### Frontend JavaScript Functions

The frontend JavaScript is located in:

```text
week_3/frontend/src/templates/chat_page.html
```

Important JavaScript functions include:

| Function            | Purpose                                                 |
| ------------------- | ------------------------------------------------------- |
| `addMessage()`      | Adds user and bot messages to the chat history          |
| `extractPdfText()`  | Extracts readable text from an uploaded PDF file        |
| Form submit handler | Sends the user message, PDF text, and file name as JSON |

The PDF extraction is handled in the browser before the data is sent to the backend.

#### Backend Service

The backend service is located in:

```text
week_3/backend/src/app.py
```

Main backend routes:

| Method | Endpoint | Description                                                         |
| ------ | -------- | ------------------------------------------------------------------- |
| `GET`  | `/`      | Health check endpoint                                               |
| `POST` | `/chat`  | Receives JSON data, calls the Week 2 module, and returns the result |

#### `GET /`

This endpoint checks whether the backend is running.

Expected response:

```json
{
  "status": "Backend is running"
}
```

#### `POST /chat`

This endpoint receives the user message and extracted PDF text from the frontend.

Expected request format:

```json
{
  "message": "hello",
  "pdf_text": "text extracted from PDF",
  "file_name": "resume.pdf"
}
```

Expected response format:

```json
{
  "reply": "Week 2 analysis result",
  "user_message": "hello",
  "file_name": "resume.pdf"
}
```

The backend writes the received PDF text into the Week 2 resume input file and then calls the Week 2 skill-gap analysis module. The output is returned to the frontend as a JSON response.

---

### Data / Assumptions

The system uses files and logic from the previous Week 2 module.

Important Week 2 files used by the backend include:

```text
week_3/backend/src/week_2/find_skill_gaps.py
week_3/backend/src/week_2/tag_data.py
week_3/backend/src/week_2/prompt_model.py
week_3/backend/src/week_2/data/jobs_d1.db
week_3/backend/src/week_2/data/resume.txt
```

#### Data Flow

The data flow of the system is:

```text
User opens frontend in browser
↓
User types a message and optionally uploads a PDF
↓
Frontend extracts PDF text in the browser
↓
Frontend sends JSON data to the frontend /chat proxy route
↓
Frontend service forwards the JSON request to the backend service
↓
Backend receives the POST /chat request
↓
Backend calls the Week 2 skill-gap analysis module
↓
Backend returns the result as JSON
↓
Frontend displays the response in the chat history
```

#### Assumptions

The system assumes that:

* Uploaded files are PDF documents.
* Uploaded PDFs contain extractable text.
* The PDF is not password-protected.
* The PDF is not purely image-based or scanned without selectable text.
* The PDF size is reasonable for browser-based text extraction.
* The backend service is running before the frontend sends requests.
* The Week 2 module and database files exist inside the backend container.
* If a local LLM service is required, it is running on the host machine and can be accessed from Docker using `host.docker.internal`.
* The application is intended for local development and testing, not production deployment.

---

### Testing

#### Frontend Local Test

The frontend was first tested locally using Uvicorn.

Command:

```bash
cd week_3/frontend
uv run uvicorn --app-dir src main:app
```

The frontend was accessed at:

```text
http://127.0.0.1:8000
```

Frontend test cases included:

* Opening the chat page
* Confirming the Bootstrap interface loads correctly
* Checking that the chat history is scrollable
* Checking that the input section is below the chat history
* Sending a normal text message
* Uploading a PDF file
* Confirming the PDF file name is displayed
* Confirming the extracted PDF text length is shown
* Confirming the message and PDF text are prepared as JSON

#### Backend Local Test

The backend was tested locally using Uvicorn.

Command:

```bash
cd week_3/backend
uv run uvicorn --app-dir src app:app --port 8001
```

The backend health check was tested at:

```text
http://127.0.0.1:8001
```

Expected response:

```json
{
  "status": "Backend is running"
}
```

The `/chat` endpoint was tested using PowerShell:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8001/chat" -Method Post -ContentType "application/json" -Body '{"message":"hello","pdf_text":"","file_name":null}'
```

Expected result:

```text
reply
-----
gaps=[...]
```

This confirmed that the backend could receive JSON requests, call the Week 2 module, and return a response.

#### Individual Docker Test

The backend was tested as a Docker container.

Backend build and run commands:

```bash
cd week_3/backend
docker build ./ -t backend:1.0
docker run -p 8001:8001 -e OLLAMA_HOST=http://host.docker.internal:11434 backend:1.0
```

The frontend was also tested as a Docker container.

Frontend build and run commands:

```bash
cd week_3/frontend
docker build ./ -t frontend:1.0
docker run -p 8000:8000 -e BACKEND_URL=http://127.0.0.1:8001/chat frontend:1.0
```

The frontend was accessed at:

```text
http://127.0.0.1:8000
```

Successful testing showed that the frontend could send a message and PDF text to the backend and display the backend response.

#### Docker Compose Test

Both services were tested together using Docker Compose.

Command:

```bash
cd week_3
docker compose up --build
```

The running services were checked using:

```bash
docker compose ps
```

Expected result:

```text
NAME                SERVICE    STATUS    PORTS
week_3-backend-1    backend    Up        0.0.0.0:8001->8001/tcp
week_3-frontend-1   frontend   Up        0.0.0.0:8000->8000/tcp
```

Successful communication was confirmed through backend logs:

```text
POST /chat endpoint called
POST /chat HTTP/1.1 200 OK
```

The frontend also displayed the backend result in the chat history. This confirmed that both containers were communicating correctly through the Docker Compose network.

---

### Limitations

This system has several limitations:

* Chat history is only stored temporarily in the browser and is not saved permanently.
* There is no user authentication or account system.
* The application does not currently store chat messages in a database.
* PDF extraction may not work well for scanned PDFs or image-based PDFs.
* Very large PDF files may take longer to extract and process.
* The quality of the chatbot response depends on the Week 2 module and the available job database.
* The backend currently calls the Week 2 module through a subprocess, which is simple but may not be the most efficient long-term design.
* Error handling is basic and could be improved for production use.
* The frontend is simple and focuses on functionality rather than advanced design.
* The current system is designed for local development and testing, not cloud deployment or production use.

---

### Architecture Reflection

#### Design Choices

I chose a microservices-style architecture by separating the frontend and backend into different services. This separation makes the system easier to understand and maintain because each service has a clear responsibility. The frontend focuses on user interaction, PDF upload, PDF text extraction, and displaying chat messages. The backend focuses on receiving requests, running the Week 2 analysis module, and returning the result.

Each service has its own Dockerfile. This allows the frontend and backend to be built independently and makes the setup more reproducible. If another user wants to run the project, they do not need to manually install all dependencies on their machine because Docker handles the environment setup.

Docker Compose was used to run the services together. This is useful because both services can share the same Docker network and communicate using service names such as `backend`. This avoids relying on hard-coded local machine addresses and makes the system closer to a real deployment setup.

#### Trade-offs

One trade-off is that Docker Compose adds more setup complexity compared to running the frontend and backend directly with Uvicorn. However, the benefit is that Docker Compose makes the project easier to reproduce and ensures that both services run in a consistent environment.

Another trade-off is that the frontend is built using simple HTML, Bootstrap, and JavaScript instead of a modern frontend framework. This makes the project easier to complete within the module timeline and keeps the code understandable. However, it also means the frontend has limited structure compared to a larger React or Vue application.

The backend currently calls the Week 2 module using a subprocess. This was chosen because it allowed the previous Week 2 code to be reused with minimal changes. However, this approach is less clean than refactoring the Week 2 logic into reusable Python functions. In the future, direct function calls would make the backend easier to test and maintain.

#### Improvements

If given more time, I would improve the system by adding a database to store chat history and uploaded file metadata. I would also add user authentication so that different users can manage their own chat sessions. The frontend could be improved with a more advanced framework and better loading indicators while the backend is processing requests.

I would also improve PDF handling by supporting OCR for scanned PDFs and adding validation for PDF size and file type. The backend integration could be improved by refactoring the Week 2 module into cleaner reusable functions instead of running it through a subprocess. Finally, the application could be deployed to a cloud platform so that it can be accessed outside the local development environment.
