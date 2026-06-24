import json
import os
import urllib.error
import urllib.request
from pathlib import Path

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

# This follows the requirement because the backend URL is not hard-coded 
# in the HTML or JavaScript. It is loaded from .env using python-dotenv.
