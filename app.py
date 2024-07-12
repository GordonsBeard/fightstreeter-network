"""The flask module that powers the website"""

import sqlite3
from datetime import datetime, timedelta

# import jinja2
import pandas as pd
import plotly.express as px  # type: ignore[import-untyped]
import plotly.graph_objects as go  # type: ignore[import-untyped]
import pytz
from flask import Flask, render_template

from cfn_secrets import FUNNY_ANIMALS
from constants import charid_map, league_ranks

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
def player_stats(player_id: str, disp_name: str) -> str:
    """stats page for a single player"""
    if len(player_id) != 10 or not player_id.isnumeric():
        return render_template("player_lp_history_error.html", player_id=player_id)

    conn: sqlite3.Connection = sqlite3.connect("cfn-stats.db")

    df: pd.DataFrame = pd.read_sql_query(
        "SELECT player_id, char_id, lp, mr, "
        "[date]"
        f" FROM ranking WHERE player_id='{player_id}'"
        " AND lp > 0",
        conn,
    )

    if not df["lp"].any():
        return render_template("player_lp_history_error.html", player_id=player_id)

    df["char_id"] = df["char_id"].replace(charid_map)

    last_30_days = pd.to_datetime(
        datetime.now(tz=pytz.timezone("America/Los_Angeles")) - timedelta(days=30)
    )

    df["date"] = pd.to_datetime(df["date"])

    df = df[df["date"] > last_30_days]

    lp_fig = px.line(
        df,
        x="date",
        y="lp",
        title=f"{disp_name}: League Points",
        color="char_id",
        template="plotly_dark",
        line_shape="spline",
    )

    lp_fig.update_yaxes(
        tickvals=list(league_ranks.keys()), ticktext=list(league_ranks.values())
    )

    lp_fig_html: str = lp_fig.to_html(full_html=False)

    df = df.where(df["mr"] > 0)

    if len(df["mr"]) > 0:
        mr_fig = px.line(
            df,
            x="date",
            y="mr",
            title=f"{disp_name}: Master Rate",
            color="char_id",
            template="plotly_dark",
            line_shape="spline",
        )

        mr_fig_html: str = mr_fig.to_html(full_html=False)

    return render_template(
        "player_lp_history.html", lp_fig=lp_fig_html, mr_fig=mr_fig_html
    )


@app.route("/rankings")
def club_ranking() -> str:
    """show lp history of all players in the club"""
    conn: sqlite3.Connection = sqlite3.connect("cfn-stats.db")

    fig = go.Figure()

    df: pd.DataFrame = pd.read_sql_query(
        "SELECT * FROM ranking WHERE player_id IN (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, \
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) AND lp >= 0",
        conn,
        params=(tuple(FUNNY_ANIMALS)),
    )

    df["char_id"] = df["char_id"].replace(charid_map)

    lp_fig_html: str | None = None
    player_id: str = "3425126856"
    df = df.where(df["player_id"] == player_id)

    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["lp"],
            name=player_id,
            line={"color": "firebrick", "width": 4},
        )
    )
    player_id = "3469051697"
    df = df.where(df["player_id"] == player_id)
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["lp"],
            name=player_id,
            line={"color": "royalblue", "width": 4},
        )
    )

    fig.update_layout(
        title="FunnyAnimals LP Board", xaxis_title="Date", yaxis_title="League Points"
    )

    lp_fig_html = fig.to_html(full_html=False)

    return render_template(
        "ranked_placements.html",
        lp_fig=lp_fig_html,
    )
