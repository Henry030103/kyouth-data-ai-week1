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

