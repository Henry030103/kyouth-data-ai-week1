import re
import time
import sqlite3
from typing import Any, Dict, List
from pydantic import BaseModel


RESUME_PATH = "data/resume.txt"
DB_PATH = "data/jobs_d1.db"


class SkillGapResult(BaseModel):         # Defines the output structure of the function
    gaps: List[str]                      # ['docker', 'java', 'mongodb', 'sql']
    time: int
    tokens: int
    input_tokens: int                    # input_tokens  = resume + job skills
    output_tokens: int                   # output_tokens = skill gaps result
    skill_demand: Dict[str, int]
    top_demand_skills: List[str]
    demand_difference: int
    prompt_optimization: Dict[str, Any]
    algorithm_optimization: Dict[str, Any]
    jailbreak_safety: Dict[str, Any]


def estimate_tokens(text: str) -> int:
    return len(text.split()) * 4


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("c++", "cplusplus")
    text = text.replace("c#", "csharp")
    text = re.sub(r"[^a-z0-9+#./\-\s]", " ", text)
    text = text.replace("cplusplus", "c++")
    text = text.replace("csharp", "c#")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_skill(skill: str) -> str:
    skill = skill.lower().strip()                 # Lowercase and remove outside spaces.
    skill = skill.strip(" .,:;()[]{}")
    skill = re.sub(r"\s+", " ", skill)
    return skill


def split_skill(raw_skill: str) -> List[str]:
    skill = normalize_skill(raw_skill)

    if not skill:
        return []

    if "not specified" in skill:
        return []

    if skill in ["none", "null", "n/a", "na"]:
        return []

    if skill in ["a/b testing", "ci/cd"]:
        return [skill]

    if "/" in skill:
        parts = skill.split("/")
        return [normalize_skill(part) for part in parts if normalize_skill(part)]

    return [skill]


def read_resume(input_file_path: str) -> str:
    try:
        with open(input_file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as error:
        print(f"Could not read resume file: {error}")
        return ""


def check_jailbreak_safety(resume_text: str) -> Dict[str, Any]:   # Bonus part
    suspicious_phrases = [                         # These are phrases commonly used in prompt injection or jailbreak attempts
        "ignore previous instructions",
        "ignore all instructions",
        "system prompt",
        "developer message",
        "reveal your prompt",
        "jailbreak",
        "act as dan",
        "do anything now",
        "bypass safety",
    ]

    text = resume_text.lower()                # lowercases the resume and creates an empty list for detected phrases.
    detected = []

    for phrase in suspicious_phrases:           # check whether any suspicious phrase appears in resume
        if phrase in text:
            detected.append(phrase)

    return {
        "safe_to_process": len(detected) == 0,
        "detected_phrases": detected,
        "mitigation": "Resume text is processed using deterministic regex and is not sent to a non-Gemini model.",
    }


def get_skill_demand(db_url: str) -> Dict[str, int]:   # function reads the database and counts how often each skill appears.
    skill_demand = {}

    try:
        conn = sqlite3.connect(db_url)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT tech_stack
            FROM jobs
            WHERE tech_stack IS NOT NULL
            AND TRIM(tech_stack) != ''
            """
        )

        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            tech_stack = row[0]

            for raw_skill in tech_stack.split(","):
                skills = split_skill(raw_skill)     # cleans and splits slash-based skills if needed.

                for skill in skills:
                    if skill:
                        skill_demand[skill] = skill_demand.get(skill, 0) + 1

    except Exception as error:
        print(f"Database error handled safely: {error}")

    return dict(sorted(skill_demand.items()))


def skill_exists_in_resume(skill: str, resume_text: str) -> bool:
    skill = normalize_skill(skill)

    if skill == "c++":
        return "c++" in resume_text or "c/c++" in resume_text

    if skill == "c#":
        return "c#" in resume_text

    pattern = r"(?<![a-z0-9+#])" + re.escape(skill) + r"(?![a-z0-9+#])"
    return re.search(pattern, resume_text) is not None


def benchmark_algorithm(job_skills: List[str]) -> Dict[str, Any]:  # Bonus part, proves that the optimized algorithm is faster than a naive algorithm.
    expanded_skills = job_skills * 3000     # repeats the skill list many times to make the time difference easier to measure

    start = time.perf_counter()
    naive_unique = []

    for skill in expanded_skills:
        if skill not in naive_unique:
            naive_unique.append(skill)

    naive_time = (time.perf_counter() - start) * 1000    #uses list to remove duplicate

    start = time.perf_counter()
    optimized_unique = sorted(set(expanded_skills))
    optimized_time = (time.perf_counter() - start) * 1000

    if naive_time == 0:
        improvement = 0
    else:
        improvement = ((naive_time - optimized_time) / naive_time) * 100

    return {
        "naive_time_ms": round(naive_time, 3),
        "optimized_time_ms": round(optimized_time, 3),
        "time_reduction_percent": round(improvement, 2),
        "proof": "Optimized version uses set() instead of repeated list membership checks.",
    }


def prompt_optimization_proof(resume_text: str, job_skills: List[str]) -> Dict[str, Any]:
    baseline_prompt = f"""
You are an advanced career advisor and skill gap analysis assistant.
Please carefully read the resume below, then compare it against all job market skills.
Explain the missing technical skills in a clear and detailed way.

Resume:
{resume_text}

Job Market Skills:
{", ".join(job_skills)}
"""

    optimized_prompt = f"""
Find missing skills only.
Resume: {resume_text[:1000]}
Skills: {",".join(job_skills)}
"""

    baseline_tokens = estimate_tokens(baseline_prompt)  #these 2 estimate tokens for both prompt
    optimized_tokens = estimate_tokens(optimized_prompt)

    if baseline_tokens == 0:
        reduction = 0
    else:
        reduction = ((baseline_tokens - optimized_tokens) / baseline_tokens) * 100

    return {
        "baseline_tokens": baseline_tokens,
        "optimized_tokens": optimized_tokens,
        "token_reduction_percent": round(reduction, 2),
        "proof": "Optimized prompt removes explanation request and limits resume length.",
    }


def find_skill_gaps(input_file_path: str, db_url: str) -> SkillGapResult:  # require function signature, which means program must hv a function named find_skill_gap, and function must accept two inputs and return a SkillGapResult.
    start_time = time.time()     # start measuring time

    resume_raw = read_resume(input_file_path)    # read resume
    safety_result = check_jailbreak_safety(resume_raw)   # check if resume contains suspicious jailbreak phases

    resume_text = normalize_text(resume_raw)    # clean resume text

    skill_demand = get_skill_demand(db_url)     # Read job skills from the database and count demand.
    job_skills = sorted(skill_demand.keys())    # Get only the skill names and sort them.

    gaps = []

    for skill in job_skills:
        if not skill_exists_in_resume(skill, resume_text):
            gaps.append(skill)

    gaps = sorted(set(gaps))      # removes duplicates and sorts the gaps

    input_text = resume_text + " " + " ".join(job_skills)
    output_text = " ".join(gaps)

    input_tokens = estimate_tokens(input_text)       # Bonus requirement about token counting
    output_tokens = estimate_tokens(output_text)
    total_tokens = input_tokens + output_tokens

    sorted_demand = sorted(        # Sort skill demand by Highest count first and alphabetical order if same count
        skill_demand.items(),
        key=lambda item: (-item[1], item[0])
    )

    top_demand_skills = [
        f"{skill}: {count}" for skill, count in sorted_demand[:5]  # take top 5 most demanded skills
    ]

    if skill_demand:
        demand_difference = max(skill_demand.values()) - min(skill_demand.values())
    else:
        demand_difference = 0     # calculates the difference between highest demand and lowest demand.

    prompt_proof = prompt_optimization_proof(resume_text, job_skills)
    algorithm_proof = benchmark_algorithm(job_skills)

    time_used = int((time.time() - start_time) * 1000)

    return SkillGapResult(
        gaps=gaps,
        time=time_used,
        tokens=total_tokens,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        skill_demand=skill_demand,
        top_demand_skills=top_demand_skills,
        demand_difference=demand_difference,
        prompt_optimization=prompt_proof,
        algorithm_optimization=algorithm_proof,
        jailbreak_safety=safety_result,
    )


def main():
    result = find_skill_gaps(RESUME_PATH, DB_PATH)

    print(f"gaps={result.gaps} time={result.time} tokens={result.tokens}")
    print(f"input_tokens={result.input_tokens} output_tokens={result.output_tokens}")
    print(f"top_demand_skills={result.top_demand_skills}")
    print(f"demand_difference={result.demand_difference}")
    print(f"prompt_optimization={result.prompt_optimization}")
    print(f"algorithm_optimization={result.algorithm_optimization}")
    print(f"jailbreak_safety={result.jailbreak_safety}")


if __name__ == "__main__":
    main()
