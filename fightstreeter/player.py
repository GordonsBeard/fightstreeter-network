"""player stats"""

import sqlite3

import pandas as pd
import plotly.express as px  # type: ignore[import-untyped]
from flask import Blueprint, render_template

from constants import charid_map, league_ranks
from fightstreeter import db

bp = Blueprint("player", __name__, url_prefix="/u")


@bp.route("/<string:player_id>")
def homepage(player_id: str) -> str:
    """dashboard page for a single player"""
    if len(player_id) != 10 or not player_id.isnumeric():
        return render_template("player_lp_history_error.html.j2", player_id=player_id)

    player_name_sql: str = (
        """SELECT cm.player_name
            FROM club_members cm
            WHERE player_id = ?;"""
    )

    name = db.query_db(player_name_sql, (player_id,), one=True)

    return render_template(
        "player/player_homepage.html.j2", player_name=name, player_id=player_id
    )


@bp.route("/<string:player_id>/graph")
def old_graph(player_id: str) -> str:
    """shows the old/simple graph"""
    if len(player_id) != 10 or not player_id.isnumeric():
        return render_template("player_lp_history_error.html.j2", player_id=player_id)

    conn: sqlite3.Connection = sqlite3.connect("cfn-stats.db")

    df: pd.DataFrame = pd.read_sql_query(
        "SELECT r.player_id, r.char_id, r.lp, r.mr, r.[date]"
        f" FROM ranking r WHERE r.player_id='{player_id}'"
        " AND r.lp > 0",
        conn,
    )

    if not df["lp"].any():
        return render_template(
            "player/player_lp_history_error.html.j2", player_id=player_id
        )

    df["char_id"] = df["char_id"].replace(charid_map)

    df["date"] = pd.to_datetime(df["date"], format="ISO8601", utc=True)

    lp_fig = px.line(
        df,
        x="date",
        y="lp",
        title=f"{player_id}: League Points",
        color="char_id",
        template="plotly_dark",
        line_shape="spline",
    )

    lp_fig.update_yaxes(
        tickvals=list(league_ranks.keys()),
        ticktext=[x["name"] for x in league_ranks.values()],
    )

    lp_fig_html: str = lp_fig.to_html(full_html=False)

    mr_fig_html: str = ""

    df = df[df["mr"] > 0]
    if len(df["mr"]) > 0:
        mr_fig = px.line(
            df,
            x="date",
            y="mr",
            title=f"{player_id}: Master Rate",
            color="char_id",
            template="plotly_dark",
            line_shape="spline",
        )

        mr_fig_html = mr_fig.to_html(full_html=False)

    return render_template(
        "player/player_lp_history.html.j2", lp_fig=lp_fig_html, mr_fig=mr_fig_html
    )
