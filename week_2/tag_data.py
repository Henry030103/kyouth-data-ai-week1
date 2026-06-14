import os
import time
import sqlite3
from dotenv import load_dotenv
from google import genai


MODEL_NAME = "gemini-2.5-flash-lite"
DB_PATH = "data/jobs_d1.db"                 # Location of the database
RATE_LIMIT_FILE = "rate_limits.txt"


def estimate_tokens(text: str) -> int:       # This function estimates token usage.
    words = text.split()
    return len(words) * 4                    # This assumes each word uses around 4 tokens. This follows the bonus instruction if token count is not returned.


def get_rate_limit(model_name: str) -> int:
    try:
        with open(RATE_LIMIT_FILE, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.split()

                if len(parts) == 4 and parts[0] == model_name:
                    rpm = int(parts[1])
                    return rpm

    except Exception:
        print("Could not read rate_limits.txt. Using default RPM = 5.")

    return 5


def create_prompt(rows):
    prompt = """
Extract the technical stack from each job description.

Return ONLY in this format:
source_id | skill1, skill2, skill3

Rules:
- One line for each job.
- Do not include explanation.
- Do not include soft skills.
- If no technical stack is found, write: Not specified.

Jobs:
"""

    for source_id, job_title, description in rows:
        prompt += f"""
Source ID: {source_id}
Job Title: {job_title}
Description: {description[:1000]}
---
"""

    return prompt


def call_gemini(prompt: str):
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        return "", 0, "GOOGLE_API_KEY not found in .env file."

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        response_text = response.text or ""

        if response.usage_metadata:
            total_tokens = response.usage_metadata.total_token_count
        else:
            total_tokens = estimate_tokens(prompt) + estimate_tokens(response_text)

        return response_text, total_tokens, None

    except Exception as error:
        return "", estimate_tokens(prompt), str(error)


def parse_response(response_text: str):                  # This function reads Gemini’s answer.
    results = {}

    lines = response_text.splitlines()

    for line in lines:
        if "|" in line:
            source_id, tech_stack = line.split("|", 1)
            source_id = source_id.strip()
            tech_stack = tech_stack.strip()

            if source_id and tech_stack:
                results[source_id] = tech_stack

    return results


def tag_data(db_url: str):
    start_time = time.time()
    total_tokens = 0

    rpm = get_rate_limit(MODEL_NAME)
    batch_size = max(1, min(5, rpm // 2))
    retry_seconds = int(60 / rpm) + 2

    try:
        conn = sqlite3.connect(db_url)                 # This connects to the database and prepares SQL commands.
        cursor = conn.cursor()

    except Exception as error:
        print(f"Database connection failed: {error}")
        return

    try:
        while True:
            cursor.execute(                                 # This selects jobs where tech_stack is empty. It does not select jobs that already have tech_stack.
                """
                SELECT source_id, job_title, description           
                FROM jobs
                WHERE tech_stack IS NULL OR TRIM(tech_stack) = ''
                LIMIT ?
                """,
                (batch_size,),
            )

            rows = cursor.fetchall()                       # This gets the selected rows from the database.

            if not rows:
                total_time = (time.time() - start_time) * 1000
                print("No data to tag")
                print(f"Total tokens used: {total_tokens}, took {total_time:.3f}ms")
                break

            prompt = create_prompt(rows)

            response_text, tokens_used, error = call_gemini(prompt)
            total_tokens += tokens_used

            if error:
                print(f"Attempt 1 failed: {error}")
                print(f"Waiting {retry_seconds} seconds before retrying...")
                time.sleep(retry_seconds)

                response_text, tokens_used, error = call_gemini(prompt)
                total_tokens += tokens_used

                if error:
                    print(f"Attempt 2 failed: {error}")
                    break

            results = parse_response(response_text)

            for source_id, job_title, description in rows:
                source_id_text = str(source_id)

                tech_stack = results.get(source_id_text, "Not specified")

                cursor.execute(                            # This updates the tech_stack column for one job.
                    """
                    UPDATE jobs
                    SET tech_stack = ?
                    WHERE source_id = ?
                    """,
                    (tech_stack, source_id),
                )

                print(f"Analyzed Job {source_id}: {tech_stack}")

            conn.commit()

            time.sleep(retry_seconds)

    except Exception as error:
        print(f"Unexpected error handled safely: {error}")

    finally:
        conn.close()


def main():
    tag_data(DB_PATH)


if __name__ == "__main__":
    main()