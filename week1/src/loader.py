import json
import sqlite3
from pathlib import Path


def create_jobs_table(cursor):       # create a function that prepares the jobs table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            source_id TEXT PRIMARY KEY,         
            job_title TEXT NOT NULL,
            company TEXT NOT NULL,
            description TEXT NOT NULL,
            tech_stack TEXT
        )
        """
    )


def load_all_jsons(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    db_path = output_dir / "jobs.db"            #The database will be saved as data/3_gold/jobs.db

    json_files = list(input_dir.glob("*.json"))

    total = len(json_files)
    inserted = 0
    skipped = 0

    print("🥇 Gold:...")

    connection = sqlite3.connect(db_path)       #open database and prepare to run the SQL commands
    cursor = connection.cursor()

    create_jobs_table(cursor)

    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        cursor.execute(
            """
            INSERT OR IGNORE INTO jobs (
                source_id,
                job_title,
                company,
                description,
                tech_stack
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                data["source_id"],
                data["job_title"],
                data["company"],
                data["description"],
                data.get("tech_stack", ""),
            ),
        )

        if cursor.rowcount == 1:              #If one row was inserted, count it as inserted.
            print(f"✅ Inserted: {json_file.name}")
            inserted += 1
        else:
            print(f"⏭️ Skipped duplicate: {json_file.name}")
            skipped += 1

    connection.commit()
    connection.close()

    print("\n📊 Gold Summary:")
    print(f"Total: {total} | Inserted: {inserted} | Skipped: {skipped}")