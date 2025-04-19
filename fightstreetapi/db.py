"""database handling"""

import sqlite3

from flask import current_app, g


def get_db() -> sqlite3.Connection:
    """grabs a reused connection to the database"""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_=None):
    """closes the connection once its no longer needed"""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    """Query the database and get back just a value or the list of rows"""
    db = get_db()
    results = db.execute(query, args).fetchall()
    return (results[0] if results else None) if one else results


def insert_db(query, args=()) -> bool:
    """Insert some data into the database"""
    success = False
    db = get_db()
    try:
        db.execute(query, args)
        db.commit()
        success = True
    except sqlite3.Error as error:
        print(error)
        success = False
    return success


def latest_stats_date() -> str:
    """Get's the date of the latest stats insert"""
    if "latest" not in g:
        row = query_db("SELECT MAX(date) as date FROM last_update;", one=True)
        g.latest = row["date"] if row else "None"  # type: ignore
    return g.latest


def dates_with_data() -> list[str]:
    """Returns a list of dates the site has data for"""
    if "dates_with_data" not in g:
        sql = """SELECT DISTINCT date FROM ranking ORDER BY date DESC;"""
        results = query_db(sql)
        dates: list[str] = [x[0] for x in results] if results else []
        g.dates_with_data = dates
    return g.dates_with_data


def init_app(app):
    """init the database module"""
    app.teardown_appcontext(close_db)
