\# K-Youth Data AI - Week 1 Data Pipeline



\## Project Description



This project implements a simple local data pipeline for processing job listing data. The pipeline follows the Medallion Architecture, where data moves through different layers from raw source files to a final database.



The goal of this project is to extract job listing information from raw `.mhtml` files, convert them into readable `.html` files, clean and structure the data into `.json` files, load the structured data into a SQLite database, and finally generate a data quality report.



The pipeline contains four main stages:



1\. Bronze Layer: Extract `.mhtml` files into `.html`

2\. Silver Layer: Process `.html` files into structured `.json`

3\. Gold Layer: Load `.json` files into SQLite database

4\. Profiling: Generate data quality metrics from the database



\---



\## Project Structure



```text

week1/

├── data/

│   ├── 0\_source/          # Raw MHTML files

│   ├── 1\_bronze/          # Extracted HTML files

│   ├── 2\_silver/          # Cleaned JSON files

│   └── 3\_gold/            # SQLite database

├── src/

│   ├── ingestor.py        # Extracts MHTML to HTML

│   ├── processor.py       # Cleans HTML and converts to JSON

│   ├── loader.py          # Loads JSON data into SQLite

│   └── profiler.py        # Runs data quality checks

├── main.py                # CLI orchestration file

├── pyproject.toml

├── uv.lock

├── README.md

└── .python-version

---

## Technical Reflections

### Day 1: The Extractor - Medallion and Lakehouses

It is useful to keep the original raw files because they act as the source of truth. If something goes wrong later during cleaning or loading, I can return to the original `.mhtml` files and re-run the pipeline without needing to collect the data again. This makes debugging and recovery easier because each layer stores a different stage of the data.

Keeping raw data also follows the idea of a data lake, where unprocessed data is stored before being transformed. Instead of directly inserting raw data into the database, the Bronze Layer gives the project a safer and more organized starting point.

### Day 2: Treatment Plant - ETL vs ELT and Scale

Cloud systems may prefer loading raw data first before cleaning it because storage is cheap and transformations can be performed later using scalable tools. This approach is known as ELT, where data is extracted, loaded, and then transformed. It allows companies to keep the original data while applying different transformations for different use cases.

When processing files sequentially, the system can become slow because each file is handled one by one. Distributed processing helps by splitting the workload across many machines or workers, allowing large amounts of data to be processed faster and more reliably.

### Day 3: The Blueprint and The Vault - Storage and Contracts

If an important field such as `job_title` disappears, the system should fail early or skip the invalid record instead of silently inserting null values into the database. This is important because incomplete records can break dashboards, reports, or downstream analytics.

Using `INSERT OR IGNORE` helps prevent duplicate records because the database uses `source_id` as the primary key. If the same job appears again, SQLite ignores the duplicate instead of inserting it again. This makes the loading process idempotent, meaning the script can be run multiple times without creating duplicate records.

### Day 4: The QA Inspector and Orchestrator - Orchestration and DAGs

If `processor.py` crashes halfway, the pipeline may only process part of the data, causing incomplete outputs in the Silver Layer. Manual retries can be unreliable because the user may forget which step failed or rerun the wrong stage.

Automated orchestration tools such as Airflow are more reliable because they manage task order, dependencies, retries, and failure handling. In this project, `main.py` acts as a simple manual orchestrator, while the `all` command runs the full pipeline in sequence.
