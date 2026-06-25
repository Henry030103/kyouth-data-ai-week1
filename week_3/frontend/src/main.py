import json
import os
import urllib.error
import urllib.request
from pathlib import Path
import urllib.parse

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent
WEEK_3_DIR = FRONTEND_DIR.parent

load_dotenv(WEEK_3_DIR / ".env")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chat_page.html",
        context={},
    )


@app.post("/chat")
async def proxy_chat(request: Request):
    backend_url = os.getenv("BACKEND_URL", "http://backend:8001/chat")
    payload = await request.json()

    try:
        request_data = json.dumps(payload).encode("utf-8")

        backend_request = urllib.request.Request(
            backend_url,
            data=request_data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(backend_request, timeout=300) as response:
            response_body = response.read().decode("utf-8")
            response_data = json.loads(response_body)

            return JSONResponse(
                status_code=response.status,
                content=response_data,
            )

    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8")

        return JSONResponse(
            status_code=error.code,
            content={
                "reply": "Backend returned an error.",
                "error": error_body,
            },
        )

    except Exception as error:
        return JSONResponse(
            status_code=502,
            content={
                "reply": "Frontend could not reach the backend service.",
                "error": str(error),
            },
        )

@app.get("/analytics")
async def proxy_analytics(search: str = ""):
    backend_chat_url = os.getenv("BACKEND_URL", "http://backend:8001/chat")
    backend_analytics_url = backend_chat_url.replace("/chat", "/analytics")

    if search:
        backend_analytics_url += "?search=" + urllib.parse.quote(search)

    try:
        backend_request = urllib.request.Request(
            backend_analytics_url,
            method="GET",
        )

        with urllib.request.urlopen(backend_request, timeout=60) as response:
            response_body = response.read().decode("utf-8")
            response_data = json.loads(response_body)

            return JSONResponse(
                status_code=response.status,
                content=response_data,
            )

    except Exception as error:
        return JSONResponse(
            status_code=502,
            content={
                "error": str(error),
                "total_jobs": 0,
                "skill_labels": [],
                "skill_values": [],
                "job_labels": [],
                "job_values": [],
                "rows": [],
            },
        )

# This follows the requirement because the backend URL is not hard-coded 
# in the HTML or JavaScript. It is loaded from .env using python-dotenv.
