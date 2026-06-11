import json
import re        #import regular expression support
from pathlib import Path

from bs4 import BeautifulSoup
from pydantic import BaseModel


class JobListing(BaseModel):
    source_id: str
    job_title: str
    company: str
    description: str


def clean_text(text):                   # This creates a function to clean messy text.
    return " ".join(text.split())       # This removes extra spaces, new lines, and tabs.


def get_source_id(soup):
    og_url = soup.find("meta", property="og:url")

    if og_url:
        url = og_url.get("content", "")
        numbers = re.findall(r"\d+", url)

        if numbers:
            return numbers[-1]

    return ""


def get_job_title(soup):
    title = soup.find("meta", property="og:title")

    if title:
        return clean_text(title.get("content", ""))

    h1 = soup.find("h1")

    if h1:
        return clean_text(h1.get_text(" ", strip=True))

    return ""


def get_company(soup):
    company = soup.find(attrs={"data-automation": "advertiser-name"})

    if company:
        company_name = clean_text(company.get_text(" ", strip=True))

        if company_name.lower() == "private advertiser":
            return ""

        return company_name

    return "" # if no company found, return empty text


def get_description(soup):
    description = soup.find(attrs={"data-automation": "jobAdDetails"})

    if description:
        return clean_text(description.get_text(" ", strip=True))

    return ""


def process_one_html(html_file):
    html_text = html_file.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html_text, "html.parser")

    return JobListing(
        source_id=get_source_id(soup),
        job_title=get_job_title(soup),
        company=get_company(soup),
        description=get_description(soup),
    )


def process_all_html(input_dir, output_dir):             # main day 2 function, it processes all .html files in bronze folder
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    html_files = list(input_dir.glob("*.html"))

    total = len(html_files)
    processed = 0
    skipped = 0

    print("🥈 Silver:...")

    for html_file in html_files:
        job = process_one_html(html_file)       # process one HTML file and stores the extracted result in job

        if not job.source_id or not job.job_title or not job.company or not job.description:   # checks whether any required field is missing, if empty, the file is skipped
            print(f"⚠️ Missing required data in: {html_file.name}")
            skipped += 1
            continue

        output_file = output_dir / f"{html_file.stem}.json"

        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(job.model_dump(), file, ensure_ascii=False, indent=4)

        print(f"✅ Processed: {html_file.name}")
        processed += 1

    print("\n📊 Silver Summary:")
    print(f"Total: {total} | Processed: {processed} | Skipped: {skipped}")