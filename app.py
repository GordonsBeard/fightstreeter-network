"""The flask module that powers the website"""

# import jinja2
import dataclasses
import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px  # type: ignore[import-untyped]
import plotly.graph_objects as go  # type: ignore[import-untyped]
from flask import Flask, render_template
from pandas import DataFrame

from awards import generate_awards
from constants import FUNNY_ANIMALS, charid_map, league_ranks
from leaderboards import generate_leaderboards

app = Flask(__name__)


@app.route("/")
def index() -> str:
    """index/home"""
    conn: sqlite3.Connection = sqlite3.connect("cfn-stats.db")

    inactive_player_scores: str = (
        """SELECT hs.date, hs.player_id, hs.player_name, hs.selected_char as char_id, hs.selected_char as char_name, hs.lp, hs.mr
        FROM historic_stats hs
        WHERE date = (SELECT MAX(date) FROM historic_stats)
        GROUP BY hs.date, hs.player_id
        ORDER BY hs.player_name COLLATE NOCASE;"""
    )

    # historic stats table gets us the ranks of every player's current char (all phases)
    inactive_df: pd.DataFrame = pd.read_sql_query(inactive_player_scores, conn)
    inactive_df["char_name"] = inactive_df["char_id"].replace(charid_map)
    inactive_df["date"] = pd.to_datetime(inactive_df["date"], format="ISO8601")

    conn.close()

    member_list = [
        (
            player_id,
            player_name,
            char_name.lower().replace(" ", "").replace(".", ""),
            lp,
        )
        for _, player_id, player_name, char_id, char_name, lp, _ in inactive_df.values
    ]

    return render_template(
        "index.html",
        member_list=member_list,
    )


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
        datetime.now(tz=ZoneInfo("America/Los_Angeles")) - timedelta(days=30)
    )

    df["date"] = pd.to_datetime(df["date"], format="ISO8601")

    # df = df[df["date"] > last_30_days]  # currently pulls data from last 30 days

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
        tickvals=list(league_ranks.keys()),
        ticktext=[x["name"] for x in league_ranks.values()],
    )

    # lp_fig_html: str = lp_fig.to_html(full_html=False)
    lp_fig_html: str = lp_fig.to_html(full_html=False)

    mr_fig_html: str = ""

    df = df[df["mr"] > 0]
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

        mr_fig_html = mr_fig.to_html(full_html=False)

    return render_template(
        "player_lp_history.html", lp_fig=lp_fig_html, mr_fig=mr_fig_html
    )


@app.route("/leaderboards")
def leaderboards() -> str:
    """Displays MR/LP/Kudos leaderboards and stats for the club."""

    top_10_boards, top_10_grouped = generate_leaderboards()

    awards_list = generate_awards()

    last_updated = """SELECT MAX(date) FROM last_update;"""
    conn: sqlite3.Connection = sqlite3.connect("cfn-stats.db")
    cur = conn.cursor()
    cur.execute(last_updated)
    date_fetched = cur.fetchone()

    last_updated = date_fetched[0] if date_fetched else "Never!"

    return render_template(
        "club_leaderboards.html",
        top_10_boards=top_10_boards,
        top_10_grouped=top_10_grouped,
        awards_list=awards_list,
        last_updated=last_updated,
    )


@dataclasses.dataclass
class PlayerRank:
    """Model of the player card to be displayed on ranking page."""

    player_id: str
    player_name: str
    char_ranks: list[dict[str, str]]


@app.route("/rankings")
def club_ranking() -> str:
    """show lp history of all players in the club"""
    conn: sqlite3.Connection = sqlite3.connect("cfn-stats.db")

    df: pd.DataFrame = pd.read_sql_query(
        "SELECT * FROM ranking WHERE player_id IN (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, \
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        conn,
        params=(tuple(FUNNY_ANIMALS)),
    )

    df["char_id"] = df["char_id"].replace(charid_map)

    unranked_ids: list[str] = []
    player_dfs: list[DataFrame] = []

    for player in FUNNY_ANIMALS:
        player_df = df[df["player_id"] == player]
        if len(player_df.values) == 0:
            unranked_ids.append(player)
            continue

        # pylint: disable-next=unused-variable
        newest_date = player_df.nlargest(1, "lp")["date"].values[0]
        newest_ranks_df = player_df.query("date == @newest_date")
        player_dfs.append(newest_ranks_df)

    all_players_df: DataFrame = pd.concat(player_dfs)

    all_players_df = all_players_df.sort_values(by="lp", ascending=False)

    fig = go.Figure(
        data=[
            go.Table(
                header={"values": ["Player", "Character", "League Points"]},
                cells={
                    "values": [
                        all_players_df.player_id,
                        all_players_df.char_id,
                        all_players_df.lp,
                    ]
                },
            )
        ]
    )

    player_table: str = fig.to_html(full_html=False)
    return render_template(
        "ranked_placements.html",
        player_table=player_table,
    )
