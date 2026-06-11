import sqlite3
from pathlib import Path


def run_data_profile(db_path):      #creates the function required by your instruction.
    db_path = Path(db_path)

    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")   #means if jobs.db does not exist, the program will not crash. It will just show an error message 
        return

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_records = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT
            SUM(CASE WHEN job_title IS NULL OR job_title = '' THEN 1 ELSE 0 END),
            SUM(CASE WHEN company IS NULL OR company = '' THEN 1 ELSE 0 END),
            SUM(CASE WHEN description IS NULL OR description = '' THEN 1 ELSE 0 END)
        FROM jobs
        """
    )
    missing_job_title, missing_company, missing_description = cursor.fetchone()

    cursor.execute("SELECT AVG(LENGTH(description)) FROM jobs")
    avg_description_length = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT source_id, job_title, LENGTH(description)
        FROM jobs
        ORDER BY LENGTH(description) ASC         
        LIMIT 1
        """
    )
    shortest_source_id, shortest_job_title, shortest_length = cursor.fetchone()

    cursor.execute(
        """
        SELECT source_id, job_title, LENGTH(description)
        FROM jobs
        ORDER BY LENGTH(description) DESC        
        LIMIT 1
        """
    )
    longest_source_id, longest_job_title, longest_length = cursor.fetchone()

    connection.close()

    print("--- 🔍 DATA QUALITY REPORT ---")
    print(f"📈 Total Records: {total_records}")
    print(
        "❓ Missing Values -> "
        f"job_title: {missing_job_title}, "
        f"company: {missing_company}, "
        f"description: {missing_description}"
    )
    print(f"📝 Avg Description Length: {round(avg_description_length)} chars")
    print(f"⚠️ Shortest Description: {shortest_length} chars")
    print(f"↳ source_id: {shortest_source_id} | job_title: {shortest_job_title}")
    print(f"🚨 Longest Description: {longest_length} chars")
    print(f"↳ source_id: {longest_source_id} | job_title: {longest_job_title}")