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
