## Week 3 - Full-Stack Chat Application

### Project Overview

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
