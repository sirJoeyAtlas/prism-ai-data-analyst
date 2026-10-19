import pyodbc
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Find the .env at the project root regardless of where Python is run from
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# --- Config from .env ---
SERVER = os.getenv("DB_SERVER", "localhost")
DATABASE = os.getenv("DB_NAME", "AIDataAnalyst")
DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")


def get_connection():
    if USER and PASSWORD:
        # SQL Server Authentication
        conn_str = (
            f'DRIVER={{{DRIVER}}};'
            f'SERVER={SERVER};'
            f'DATABASE={DATABASE};'
            f'UID={USER};PWD={PASSWORD};'
            f'TrustServerCertificate=yes;'
        )
    else:
        # Windows Authentication
        conn_str = (
            f'DRIVER={{{DRIVER}}};'
            f'SERVER={SERVER};'
            f'DATABASE={DATABASE};'
            f'Trusted_Connection=yes;'
            f'TrustServerCertificate=yes;'
        )
    return pyodbc.connect(conn_str, autocommit=True)


def init_db():
    """Creates the datasets and queries tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='datasets' AND xtype='U')
    BEGIN
        CREATE TABLE datasets (
            id INT IDENTITY(1,1) PRIMARY KEY,
            filename NVARCHAR(255) NOT NULL,
            filepath NVARCHAR(500) NOT NULL,
            rows_count INT,
            columns_count INT,
            profile_json NVARCHAR(MAX),
            uploaded_at DATETIME DEFAULT GETDATE()
        );
    END
    """)

    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='queries' AND xtype='U')
    BEGIN
        CREATE TABLE queries (
            id INT IDENTITY(1,1) PRIMARY KEY,
            dataset_id INT NOT NULL,
            question NVARCHAR(MAX) NOT NULL,
            generated_code NVARCHAR(MAX),
            result_json NVARCHAR(MAX),
            explanation NVARCHAR(MAX),
            success BIT DEFAULT 0,
            created_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (dataset_id) REFERENCES datasets(id)
        );
    END
    """)

    cursor.close()
    conn.close()


def save_dataset(filename, filepath, rows, cols, profile) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO datasets (filename, filepath, rows_count, columns_count, profile_json) "
        "OUTPUT INSERTED.id VALUES (?, ?, ?, ?, ?)",
        (filename, filepath, rows, cols, json.dumps(profile)),
    )
    did = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return did


def save_query(dataset_id, question, code, result, explanation, success):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO queries (dataset_id, question, generated_code, result_json, explanation, success) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (dataset_id, question, code, json.dumps(result, default=str), explanation, int(success)),
    )
    conn.commit()  # <--- Force save
    cursor.close()
    conn.close()


def get_queries(dataset_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM queries WHERE dataset_id = ? ORDER BY id DESC",
        (dataset_id,),
    )
    columns = [column[0] for column in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return rows


def list_datasets():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM datasets ORDER BY uploaded_at DESC")
    columns = [column[0] for column in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return rows