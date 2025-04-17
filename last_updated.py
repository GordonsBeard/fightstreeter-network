"""Creates the last update table and allows for easier updating of the status."""

import logging
import sqlite3
from datetime import datetime

logging.basicConfig()
logger = logging.getLogger("cfn-stats-scrape")
logger.setLevel(logging.INFO)


LAST_UPDATE_TABLE_SQL = """CREATE TABLE IF NOT EXISTS last_update (
            date TIMESTAMP PRIMARY KEY,
            download_complete INTEGER DEFAULT 0 NOT NULL,
            parsing_complete INTEGER DEFAULT 0 NOT NULL);"""


def start_last_update(date: datetime) -> None:
    """Starts the last_update log entry"""
    table_name = "instance/cfn-stats.db"
    try:
        with sqlite3.connect(table_name) as conn:
            cursor = conn.cursor()
            cursor.execute(LAST_UPDATE_TABLE_SQL)

            cursor.execute(
                """INSERT OR REPLACE 
                INTO last_update (date, download_complete, parsing_complete)
                VALUES (?, ?, ?)""",
                (date.strftime("%Y-%m-%d"), 0, 0),
            )

    except sqlite3.Error as e:
        logger.error(e)


def log_last_update(date, download_complete=False, parsing_complete=False) -> None:
    """Lets the scraper or parser signal when they're done."""
    table_name = "instance/cfn-stats.db"

    try:
        with sqlite3.connect(table_name) as conn:
            cursor = conn.cursor()
            cursor.execute(LAST_UPDATE_TABLE_SQL)

            if download_complete:
                cursor.execute(
                    """UPDATE last_update SET download_complete = 1 WHERE date = ?""",
                    (date.strftime("%Y-%m-%d"),),
                )
            elif parsing_complete:
                cursor.execute(
                    """UPDATE last_update SET parsing_complete = 1 WHERE date = ?""",
                    (date.strftime("%Y-%m-%d"),),
                )

    except sqlite3.Error as e:
        logger.error(e)
