import sys
from pathlib import Path   #This helps Python handle file and folder paths properly.

from src.ingestor import ingest_all_mhtml    # Bring functions from other Python files into main.py
from src.processor import process_all_html   # Go to src/ingestor.py, Find the function ingest_all_mhtml, Let main.py use it
from src.loader import load_all_jsons
from src.profiler import run_data_profile

SOURCE_DIR = Path("data/0_source")        # SOURCE_DIR = original .mhtml files
BRONZE_DIR = Path("data/1_bronze")        # BRONZE_DIR = extracted .html files
SILVER_DIR = Path("data/2_silver")        # SILVER_DIR = cleaned .json files
GOLD_DIR = Path("data/3_gold")            # GOLD_DIR = final database
DB_NAME = "jobs.db"                       # DB_NAME = jobs.db


def run_bronze():
    input_dir = SOURCE_DIR                       # The input folder is data/0_source
    output_dir = BRONZE_DIR                      # The output folder is data/1_bronze
    ingest_all_mhtml(input_dir, output_dir)      # Take files from data/0_source, Extract them, Save results into data/1_bronze


def run_silver():
    input_dir = BRONZE_DIR
    output_dir = SILVER_DIR
    process_all_html(input_dir, output_dir)


def run_gold():
    input_dir = SILVER_DIR
    output_dir = GOLD_DIR
    load_all_jsons(input_dir, output_dir)


def run_profiler():
    db_path = GOLD_DIR / DB_NAME
    run_data_profile(db_path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py [ingest|process|load|profile|all]")
        #print("Please provide a command.")      Use in finding bronze silver and gold
        #print("Available commands: ingest, process, load")
        return

    command = sys.argv[1]

    if command == "ingest":
        run_bronze()
    elif command == "process":
        run_silver()
    elif command == "load":
        run_gold()
    elif command == "profile":
        run_profiler()
    elif command == "all":
        run_bronze()
        run_silver()
        run_gold()
        run_profiler()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python main.py [ingest|process|load|profile|all]")


if __name__ == "__main__":           # If this file is being run directly, start the program by calling main().
    main()

