#********************************
#   William Merry
#   Year 3
#   Matric No . 12345
#********************************

import csv
import sqlite3
from pathlib import Path

# Folder locations
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR 
DATABASE = BASE_DIR / "Advancedwebtech.db"

# CSV files and their destination tables
DATASETS = {
    "sites": "FW_Fish_Sites_2026-09-21.csv",
    "counts": "FW_Fish_Counts_2026-09-21.csv",
    "individual_lengths": "FW_Fish_Individual_Lengths_2026-09-21.csv"
}

# Fields that should contain numbers
INTEGER_FIELDS = {
    "EVENT_DATE_YEAR",
    "N_SURVEYS",
    "RUN1", "RUN2", "RUN3",
    "RUN4", "RUN5", "RUN6",
    "ALL_RUNS"
}

REAL_FIELDS = {
    "FISH_LENGTH",
    "FISH_WEIGHT",
    "SURVEY_LENGTH",
    "SURVEY_WIDTH",
    "SURVEY_AREA",
    "FISHED_WIDTH",
    "FISHED_AREA",
    "SPCSNO",
    "SPCSNO_SE",
    "SPCSPV",
    "SPCSPV_SE"
}


def quote_name(name):
    """Safely quote a database column or table name."""
    return '"' + name.replace('"', '""') + '"'


def column_type(name):
    """Choose the SQLite data type."""
    if name in INTEGER_FIELDS:
        return "INTEGER"
    if name in REAL_FIELDS:
        return "REAL"
    return "TEXT"


def convert_value(value, column):
    """Convert empty values and numeric fields."""
    if value is None or value.strip() == "":
        return None

    value = value.strip()

    if column in INTEGER_FIELDS:
        return int(value)

    if column in REAL_FIELDS:
        return float(value)

    return value


def import_csv(connection, table_name, filename):
    """Read one CSV file into a SQLite table."""

    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Cannot find CSV file: {file_path}"
        )

    with open(file_path, "r", encoding="utf-8-sig",
              newline="") as file:

        reader = csv.DictReader(file)
        columns = reader.fieldnames

        if not columns:
            raise ValueError(f"No headers found in {filename}")

        # Create a table with matching CSV columns
        definitions = ", ".join(
            f"{quote_name(col)} {column_type(col)}"
            for col in columns
        )

        connection.execute(
            f"CREATE TABLE {quote_name(table_name)} "
            f"({definitions})"
        )

        # Prepare INSERT statement
        column_names = ", ".join(
            quote_name(col) for col in columns
        )

        placeholders = ", ".join(
            "?" for col in columns
        )

        insert_sql = (
            f"INSERT INTO {quote_name(table_name)} "
            f"({column_names}) VALUES ({placeholders})"
        )

        total = 0

        for row in reader:
            if None in row:
                raise ValueError(
                    f"Extra CSV fields in {filename}, "
                    f"row {total + 2}"
                )

            values = [
                convert_value(row[col], col)
                for col in columns
            ]

            connection.execute(insert_sql, values)
            total += 1

    print(f"{table_name}: {total} rows imported")
    return total


def create_indexes(connection):
    """Add indexes for later Flask filtering."""

    indexes = [
        ("sites", "SITE_ID"),
        ("sites", "REGION"),
        ("counts", "SITE_ID"),
        ("counts", "SURVEY_ID"),
        ("counts", "SURVEY_SPECIES_ID"),
        ("counts", "SPECIES_ID"),
        ("counts", "EVENT_DATE_YEAR"),
        ("individual_lengths", "SURVEY_SPECIES_ID"),
        ("individual_lengths", "SPECIES_ID")
    ]

    for table, column in indexes:
        index_name = f"idx_{table}_{column}"

        connection.execute(
            f"CREATE INDEX {quote_name(index_name)} "
            f"ON {quote_name(table)} ({quote_name(column)})"
        )


def main():
    # Build a temporary database first
    temporary_db = BASE_DIR / "fish_importing.db"

    if temporary_db.exists():
        temporary_db.unlink()

    connection = sqlite3.connect(temporary_db)

    try:
        for table, filename in DATASETS.items():
            import_csv(connection, table, filename)

        create_indexes(connection)
        connection.commit()

    except Exception:
        connection.rollback()
        connection.close()
        temporary_db.unlink(missing_ok=True)
        raise

    connection.close()

    # Replace old database only after successful import
    temporary_db.replace(DATABASE)

    print()
    print("Import completed successfully.")
    print(f"Database created: {DATABASE}")


if __name__ == "__main__":
    main()