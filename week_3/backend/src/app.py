import os
import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
WEEK_2_DIR = BASE_DIR / "week_2"
DATA_DIR = WEEK_2_DIR / "data"
RESUME_PATH = DATA_DIR / "resume.txt"


@app.get("/")
def health_check():
    return {"status": "Backend is running"}


@app.post("/chat")
async def chat(request: Request):
    print("POST /chat endpoint called", flush=True)
    
    try:
        data = await request.json()

        user_message = data.get("message", "")
        pdf_text = data.get("pdf_text", "")
        file_name = data.get("file_name", None)

        if pdf_text:
            RESUME_PATH.write_text(pdf_text, encoding="utf-8")

        result = subprocess.run(
            [sys.executable, "find_skill_gaps.py"],
            cwd=WEEK_2_DIR,
            capture_output=True,
            text=True,
            timeout=240,
        )

        if result.returncode != 0:
            return JSONResponse(
                status_code=500,
                content={
                    "reply": "Backend received the message, but Week 2 module returned an error.",
                    "user_message": user_message,
                    "file_name": file_name,
                    "error": result.stderr,
                },
            )

        output = result.stdout.strip()

        if not output:
            output = "Week 2 module ran successfully, but no output was returned."

        return {
            "reply": output,
            "user_message": user_message,
            "file_name": file_name,
        }

    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={
                "reply": "Backend error occurred while processing the request.",
                "error": str(error),
            },
        )