import os
import subprocess
import sys
from pathlib import Path

import ast
import sqlite3
from collections import Counter

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
DB_PATH = DATA_DIR / "jobs_d1.db"


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

def quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def find_column(columns: list[str], possible_names: list[str]) -> str | None:
    lower_columns = {column.lower(): column for column in columns}

    for name in possible_names:
        if name.lower() in lower_columns:
            return lower_columns[name.lower()]

    for column in columns:
        column_lower = column.lower()
        for name in possible_names:
            if name.lower() in column_lower:
                return column

    return None


def parse_skills(value) -> list[str]:
    if value is None:
        return []

    text = str(value).strip()

    if not text:
        return []

    try:
        parsed_value = ast.literal_eval(text)
        if isinstance(parsed_value, list):
            return [
                str(skill).strip().lower()
                for skill in parsed_value
                if str(skill).strip()
            ]
    except Exception:
        pass

    text = text.replace("|", ",").replace(";", ",")

    return [
        skill.strip().lower()
        for skill in text.split(",")
        if skill.strip()
    ]


@app.get("/analytics")
def get_analytics(search: str = ""):
    try:
        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        tables = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()

        if not tables:
            return {
                "total_jobs": 0,
                "skill_labels": [],
                "skill_values": [],
                "job_labels": [],
                "job_values": [],
                "rows": [],
            }

        selected_table = None

        for table in tables:
            table_name = table["name"]
            count = cursor.execute(
                f"SELECT COUNT(*) FROM {quote_identifier(table_name)}"
            ).fetchone()[0]

            if count > 0:
                selected_table = table_name
                break

        if selected_table is None:
            selected_table = tables[0]["name"]

        column_info = cursor.execute(
            f"PRAGMA table_info({quote_identifier(selected_table)})"
        ).fetchall()

        columns = [column["name"] for column in column_info]

        title_column = find_column(columns, ["title", "job_title", "position", "role"])
        company_column = find_column(columns, ["company", "company_name", "employer"])
        location_column = find_column(columns, ["location", "city", "country"])
        description_column = find_column(columns, ["description", "job_description", "details"])
        skill_column = find_column(columns, ["tech_stack", "skills", "tags", "technologies"])

        search_columns = [
            column
            for column in [
                title_column,
                company_column,
                location_column,
                description_column,
                skill_column,
            ]
            if column
        ]

        where_clause = ""
        parameters = []

        if search and search_columns:
            where_parts = [
                f"LOWER({quote_identifier(column)}) LIKE ?"
                for column in search_columns
            ]

            where_clause = "WHERE " + " OR ".join(where_parts)
            parameters = [f"%{search.lower()}%"] * len(search_columns)

        query = f"""
            SELECT *
            FROM {quote_identifier(selected_table)}
            {where_clause}
            LIMIT 100
        """

        rows = cursor.execute(query, parameters).fetchall()
        total_jobs = len(rows)

        skill_counter = Counter()
        job_counter = Counter()

        result_rows = []

        for row in rows:
            row_dict = dict(row)

            title = row_dict.get(title_column, "Unknown Job") if title_column else "Unknown Job"
            company = row_dict.get(company_column, "Unknown Company") if company_column else "Unknown Company"
            location = row_dict.get(location_column, "Unknown Location") if location_column else "Unknown Location"
            skills = row_dict.get(skill_column, "") if skill_column else ""

            job_counter[str(title)] += 1

            for skill in parse_skills(skills):
                skill_counter[skill] += 1

            result_rows.append(
                {
                    "title": str(title),
                    "company": str(company),
                    "location": str(location),
                    "skills": str(skills),
                }
            )

        top_skills = skill_counter.most_common(10)
        top_jobs = job_counter.most_common(10)

        connection.close()

        return {
            "total_jobs": total_jobs,
            "skill_labels": [skill for skill, count in top_skills],
            "skill_values": [count for skill, count in top_skills],
            "job_labels": [job for job, count in top_jobs],
            "job_values": [count for job, count in top_jobs],
            "rows": result_rows,
        }

    except Exception as error:
        return {
            "error": str(error),
            "total_jobs": 0,
            "skill_labels": [],
            "skill_values": [],
            "job_labels": [],
            "job_values": [],
            "rows": [],
        }