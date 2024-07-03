"""The flask module that powers the website"""

import sqlite3

# import jinja2
import pandas as pd
import plotly.express as px
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index() -> str:
    """index/home"""
    conn: sqlite3.Connection = sqlite3.connect("cfn-stats.db")
    cur = conn.cursor()
    cur.execute(
        "SELECT player_name, player_id FROM club_members WHERE club_id='c984cc7ce8cd44b9a209e984a73d0c9e'"
    )

    member_list = [(x[0], x[1]) for x in cur.fetchall()]

    return render_template("index.html", member_list=member_list)


@app.route("/u/<string:player_id>/<string:disp_name>")
def player_history(player_id: str, disp_name: str) -> str:
    """show lp history of all characters"""
    if len(player_id) != 10 or not player_id.isnumeric():
        return render_template("player_lp_history_error.html", player_id=player_id)

    conn: sqlite3.Connection = sqlite3.connect("cfn-stats.db")

    df: pd.DataFrame = pd.read_sql_query(
        f"SELECT * FROM ranking WHERE player_id='{player_id}'", conn
    )

    fig = px.line(
        df, x="date", y="lp", title=f"{disp_name}: League Points", color="char_id"
    )
    fig_html: str = fig.to_html(full_html=False)

    return render_template("player_lp_history.html", fig=fig_html)
