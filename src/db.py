"""Oracle connection helper.

Credentials are read from environment variables (loaded from the project-root
`.env` file, which is git-ignored). Nothing secret is stored in this file.
"""
import os
from pathlib import Path

from dotenv import load_dotenv
import oracledb

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

USER = os.getenv("ORACLE_USER", "cinema")
PWD = os.getenv("ORACLE_PASSWORD")
DSN = os.getenv("ORACLE_DSN", "localhost:1521/FREEPDB1")


def get_conn():
    """Connect to Oracle via oracledb thin mode."""
    if not PWD:
        raise RuntimeError(
            "ORACLE_PASSWORD is not set. Create a .env file in the project root "
            "with ORACLE_USER, ORACLE_PASSWORD and ORACLE_DSN."
        )
    return oracledb.connect(user=USER, password=PWD, dsn=DSN)


def get_cursor():
    con = get_conn()
    cur = con.cursor()
    return con, cur
