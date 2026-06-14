import os
import time
import sqlite3
from dotenv import load_dotenv
from google import genai


MODEL_NAME = "gemini-2.5-flash-lite"
DB_PATH = "data/jobs_d1.db"
RATE_LIMIT_FILE = "rate_limits.txt"


def estimate_tokens(text: str) -> int:
    words = text.split()
    return len(words) * 4


def get_rate_limit(model_name: str) -> int:
    try:
        with open(RATE_LIMIT_FILE, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.split()

                if len(parts) == 4 and parts[0] == model_name:
                    return int(parts[1])

    except Exception:
        print("Could not read rate_limits.txt. Using default RPM = 5.")

    return 5


def create_baseline_prompt(rows):
    prompt = """
You are an advanced job market analysis assistant. 
Your task is to carefully read each job title and job description below, understand the technical requirements, identify all possible technologies, tools, programming languages, databases, cloud platforms, frameworks, libraries, and developer tools, and then provide the extracted technical stack for every job. Please avoid soft skills and general responsibilities. Please make sure your answer is clear and complete.

Return the result for every job.
"""

    for source_id, job_title, description in rows:
        prompt += f"""
Source ID: {source_id}
Job Title: {job_title}
Full Job Description:
{description}
---
"""

    return prompt


def create_optimized_prompt(rows):
    prompt = """
Extract technical stack only.

Format:
source_id | skill1, skill2, skill3

Rules:
- One line per job.
- No explanation.
- No soft skills.
- If none, write: Not specified.

Jobs:
"""

    for source_id, job_title, description in rows:
        prompt += f"""
ID: {source_id}
Title: {job_title}
Desc: {description[:1000]}
---
"""

    return prompt


def show_prompt_optimization_proof(cursor):
    cursor.execute(
        """
        SELECT source_id, job_title, description
        FROM jobs
        LIMIT 5
        """
    )

    sample_rows = cursor.fetchall()

    if not sample_rows:
        print("No rows available for prompt optimization proof.")
        return 0

    baseline_prompt = create_baseline_prompt(sample_rows)
    optimized_prompt = create_optimized_prompt(sample_rows)

    baseline_tokens = estimate_tokens(baseline_prompt)
    optimized_tokens = estimate_tokens(optimized_prompt)

    if baseline_tokens == 0:
        reduction_percent = 0
    else:
        reduction_percent = ((baseline_tokens - optimized_tokens) / baseline_tokens) * 100

    print("\n--- Prompt Optimization Proof ---")
    print(f"Baseline prompt tokens: {baseline_tokens}")
    print(f"Optimized prompt tokens: {optimized_tokens}")
    print(f"Token reduction: {reduction_percent:.2f}%")

    if reduction_percent > 5:
        print("Result: Token usage reduced by more than 5%.")
    else:
        print("Result: Token reduction is less than 5%.")

    return reduction_percent


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


def parse_response(response_text: str):
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


def calculate_quality(cursor):
    cursor.execute(
        """
        SELECT tech_stack
        FROM jobs
        WHERE tech_stack IS NOT NULL AND TRIM(tech_stack) != ''
        """
    )

    rows = cursor.fetchall()
    tech_stacks = [row[0].strip() for row in rows]

    total_tagged = len(tech_stacks)
    not_specified_count = tech_stacks.count("Not specified")

    duplicate_count = total_tagged - len(set(tech_stacks))

    print("\n--- Quality Measurement ---")
    print(f"Total tagged rows: {total_tagged}")
    print(f"Not specified count: {not_specified_count}")
    print(f"Duplicate tech_stack count: {duplicate_count}")

    return {
        "total_tagged": total_tagged,
        "not_specified_count": not_specified_count,
        "duplicate_count": duplicate_count,
    }


def tag_data(db_url: str):
    start_time = time.time()
    total_tokens = 0

    rpm = get_rate_limit(MODEL_NAME)
    batch_size = max(1, min(5, rpm // 2))
    retry_seconds = int(60 / rpm) + 2

    try:
        conn = sqlite3.connect(db_url)
        cursor = conn.cursor()

    except Exception as error:
        print(f"Database connection failed: {error}")
        return {
            "total_tokens": 0,
            "time_ms": 0,
            "error": str(error),
        }

    try:
        optimization_reduction = show_prompt_optimization_proof(cursor)

        while True:
            cursor.execute(
                """
                SELECT source_id, job_title, description
                FROM jobs
                WHERE tech_stack IS NULL OR TRIM(tech_stack) = ''
                LIMIT ?
                """,
                (batch_size,),
            )

            rows = cursor.fetchall()

            if not rows:
                print("\nNo data to tag")
                break

            prompt = create_optimized_prompt(rows)

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

                cursor.execute(
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

        quality_result = calculate_quality(cursor)

        total_time = (time.time() - start_time) * 1000

        print(f"\nTotal tokens used: {total_tokens}, took {total_time:.3f}ms")

        return {
            "total_tokens": total_tokens,
            "time_ms": total_time,
            "optimization_reduction_percent": optimization_reduction,
            "quality": quality_result,
        }

    except Exception as error:
        print(f"Unexpected error handled safely: {error}")

        return {
            "total_tokens": total_tokens,
            "time_ms": (time.time() - start_time) * 1000,
            "error": str(error),
        }

    finally:
        conn.close()


def main():
    result = tag_data(DB_PATH)

    print("\n--- Returned Result ---")
    print(result)


if __name__ == "__main__":
    main()