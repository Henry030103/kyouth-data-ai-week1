import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent
WEEK_3_DIR = FRONTEND_DIR.parent

load_dotenv(WEEK_3_DIR / ".env")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/")
def read_root(request: Request):
    backend_url = os.getenv("BACKEND_URL", "")

    return templates.TemplateResponse(
        request=request,
        name="chat_page.html",
        context={
            "backend_url": backend_url,
        },
    )

# This follows the requirement because the backend URL is not hard-coded 
# in the HTML or JavaScript. It is loaded from .env using python-dotenv.
