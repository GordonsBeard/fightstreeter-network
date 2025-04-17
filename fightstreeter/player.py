"""player stats"""

import sqlite3

import pandas as pd
import plotly.express as px  # type: ignore[import-untyped]
from flask import Blueprint, render_template

from constants import charid_map, league_ranks

from . import db
from .roster import generate_member_list

bp = Blueprint("player", __name__, url_prefix="/u")


@bp.route("/<string:player_id>")
def homepage(player_id: str) -> str:
    """shows the old/simple graph"""
    if len(player_id) != 10 or not player_id.isnumeric():
        return render_template("player_lp_history_error.html.j2", player_id=player_id)

    player_name_sql: str = (
        """SELECT cm.player_name
            FROM club_members cm
            WHERE player_id = ?;"""
    )
    name = db.query_db(player_name_sql, (player_id,), one=True)
    name = name["player_name"]  # type: ignore

    conn: sqlite3.Connection = db.get_db()

    df: pd.DataFrame = pd.read_sql_query(
        "SELECT r.player_id, r.char_id, r.lp, r.mr, r.[date]"
        f" FROM ranking r WHERE r.player_id='{player_id}'"
        " AND r.lp > 0",
        conn,
    )

    if not df["lp"].any():
        return render_template(
            "player/player_homepage.html.j2",
            lp_fig=None,
            mr_fig=None,
            player_name=name,
            player_id=player_id,
            member_list=generate_member_list(),
        )

    df["char_id"] = df["char_id"].replace(charid_map)
    df["date"] = pd.to_datetime(df["date"], format="ISO8601", utc=True)

    lp_fig = px.line(
        df,
        x="date",
        y="lp",
        title="League Points",
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
            title="Master Rate",
            color="char_id",
            template="plotly_dark",
            line_shape="spline",
        )

        mr_fig_html = mr_fig.to_html(full_html=False)

    return render_template(
        "player/player_homepage.html.j2",
        lp_fig=lp_fig_html,
        mr_fig=mr_fig_html,
        player_name=name,
        player_id=player_id,
        member_list=generate_member_list(),
    )
