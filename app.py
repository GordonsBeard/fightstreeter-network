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

from constants import FUNNY_ANIMALS, charid_map, league_ranks

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
        datetime.now(tz=ZoneInfo("America/Los_Angeles")) - timedelta(days=30)
    )

    df["date"] = pd.to_datetime(df["date"], format="ISO8601")

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


@app.route("/leaderboards")
def leaderboards() -> str:
    """Displays MR/LP/Kudos leaderboards and stats for the club."""

    # pylint: disable=too-many-locals

    conn: sqlite3.Connection = sqlite3.connect("cfn-stats.db")

    today: datetime = datetime.now(tz=ZoneInfo("America/Los_Angeles")).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    yesterday: datetime = today + timedelta(days=-1)

    latest_lp_scores: str = (
        """SELECT r.date, r.player_id, cm.player_name, r.char_id, r.lp, r.mr
        FROM ranking r
        INNER JOIN club_members cm ON cm.player_id = r.player_id
        GROUP BY r.date, r.player_id, r.char_id
        ORDER BY r.date DESC;"""
    )

    df: pd.DataFrame = pd.read_sql_query(latest_lp_scores, conn)
    df["char_id"] = df["char_id"].replace(charid_map)
    df["date"] = pd.to_datetime(df["date"], format="ISO8601")
    df = df[df["date"] > yesterday]

    player_ids = df["player_id"].unique()
    top_mr_df: pd.Series = pd.Series(data={})
    top_lp_df: pd.Series = pd.Series(data={})

    for player_id in player_ids:
        chars_seen: list[str] = []
        mr_chars_seen: list[str] = []
        player_df: pd.DataFrame = df[df["player_id"] == player_id]

        for i, (_, player_id, _, char_id, _, _) in enumerate(player_df.values):
            if (
                top_lp_df.empty
                or player_df["lp"].values[0] > top_lp_df["lp"]
                and char_id not in chars_seen
            ):
                chars_seen.append(char_id)
                top_lp_df = player_df.iloc[i]
            if (
                top_mr_df.empty
                or player_df["mr"].values[0] > top_mr_df["lp"]
                and char_id not in mr_chars_seen
            ):
                mr_chars_seen.append(char_id)
                top_mr_df = player_df.iloc[i]

    lp_value = f"{top_lp_df['lp']:,} LP"
    lp_player_id = top_lp_df["player_id"]
    lp_player_name = top_lp_df["player_name"]
    lp_character = top_lp_df["char_id"]

    mr_character = top_mr_df["char_id"]
    mr_value = f"{top_mr_df['mr']:,} MR"
    mr_player_id = top_mr_df["player_id"]
    mr_player_name = top_mr_df["player_name"]

    kudos_value = "100,000 Kudos"
    kudos_player_id = "123"
    kudos_player_name = "Shaymoo"
    kudos_character = "Ryu"

    podium = {
        "lp": {
            "name": "League Champion",
            "value": lp_value,
            "player_id": lp_player_id,
            "player_name": lp_player_name,
            "character": lp_character,
        },
        "mr": {
            "name": "Club Master",
            "value": mr_value,
            "player_id": mr_player_id,
            "player_name": mr_player_name,
            "character": mr_character,
        },
        "kudos": {
            "name": "Kudos Leader",
            "value": kudos_value,
            "player_id": kudos_player_id,
            "player_name": kudos_player_name,
            "character": kudos_character,
        },
    }

    return render_template("club_leaderboards.html", podium=podium)


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
    # df["date"] = pd.to_datetime(df["date"], format="ISO8601")

    unranked_ids: list[str] = []
    ranked_players: list[PlayerRank] = []
    player_dfs: list[DataFrame] = []

    for player in FUNNY_ANIMALS:
        player_df = df[df["player_id"] == player]
        if len(player_df.values) == 0:
            unranked_ids.append(player)
            continue

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
