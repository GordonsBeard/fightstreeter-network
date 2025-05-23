"""Generates the LP/MR/Kudos leaderboards"""

import dataclasses
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
from flask import Blueprint, render_template

from constants import (
    charid_map,
    fetch_league_name,
    fetch_mr_league_name,
    get_kudos_class,
    phase_dates,
)

from .awards import generate_awards
from .db import latest_stats_date, query_db

bp = Blueprint("leaderboards", __name__, url_prefix="/leaderboards")


def generate_leaderboards(
    req_datetime: datetime,
) -> tuple[
    dict[str, list[dict[str, str | int]]], dict[str, list[dict[str, str | int]]]
]:
    """Returns a tuple with the lp/mr leaderboards"""

    conn: sqlite3.Connection = sqlite3.connect("cfn-stats.db")

    latest_lp_date_selected = req_datetime.isoformat()

    latest_lp_scores: str = (
        """SELECT r.date, r.player_id, cm.player_name, r.char_id, r.lp, r.mr
        FROM ranking r
        INNER JOIN club_members cm ON cm.player_id = r.player_id
        WHERE date = ?
        GROUP BY r.date, r.player_id, r.char_id;"""
    )

    inactive_scores_date_selected = (
        req_datetime.isoformat()
        if req_datetime
        else "(SELECT MAX(date) FROM historic_stats)"
    )

    inactive_player_scores: str = (
        """SELECT hs.date, hs.player_id, hs.player_name, hs.selected_char as char_id, hs.lp, hs.mr
        FROM historic_stats hs
        WHERE date = ?
        GROUP BY hs.date, hs.player_id, char_id;"""
    )

    latest_kudos_date_selected = (
        req_datetime.isoformat()
        if req_datetime
        else "(SELECT MAX(date) FROM historic_stats)"
    )

    latest_kudos_amounts_query: str = (
        """SELECT hs.date, hs.player_id, cm.player_name, hs.total_kudos
        FROM historic_stats hs
        INNER JOIN club_members cm ON cm.player_id = hs.player_id
        WHERE date = ?;"""
    )

    # ranking table gets us the ranks from this phase
    rank_df: pd.DataFrame = pd.read_sql_query(
        latest_lp_scores, conn, params=[latest_lp_date_selected]
    )
    rank_df["char_id"] = rank_df["char_id"].replace(charid_map)
    rank_df["date"] = pd.to_datetime(rank_df["date"], format="ISO8601")

    # historic stats table gets us the ranks of every player's current char (all phases)
    inactive_df: pd.DataFrame = pd.read_sql_query(
        inactive_player_scores, conn, params=[inactive_scores_date_selected]
    )
    inactive_df["char_id"] = inactive_df["char_id"].replace(charid_map)
    inactive_df["date"] = pd.to_datetime(inactive_df["date"], format="ISO8601")
    inactive_df = inactive_df[inactive_df["lp"] != -1]

    # combine the two ranking tables to get a complete list of everyone's lp/mr
    rank_df = pd.concat([inactive_df, rank_df]).drop_duplicates().reset_index(drop=True)

    hs_df: pd.DataFrame = pd.read_sql_query(
        latest_kudos_amounts_query, conn, params=[latest_kudos_date_selected]
    )
    hs_df["date"] = pd.to_datetime(hs_df["date"], format="ISO8601")

    conn.close()

    lp_df: pd.DataFrame = rank_df.sort_values(by="lp", ascending=False)
    mr_df: pd.DataFrame = rank_df.sort_values(by="mr", ascending=False)
    mr_df = mr_df[mr_df["mr"] > 0]

    top_10_boards: dict[str, list[dict[str, str | int]]] = {
        "lp": [],
        "mr": [],
        "kudos": [],
    }

    top_10_grouped: dict[str, list[dict[str, str | int]]] = {
        "lp": [],
        "mr": [],
    }

    top_10_boards["lp"], top_10_grouped["lp"] = generate_lp_board(lp_df)
    top_10_boards["mr"], top_10_grouped["mr"] = generate_mr_board(mr_df)
    top_10_boards["kudos"] = generate_kudos_board(hs_df)

    return (top_10_boards, top_10_grouped)


def generate_mr_board(
    mr_df: pd.DataFrame,
) -> tuple[list[dict[str, str | int]], list[dict[str, str | int]]]:
    """Returns the sorted list for MR boards."""

    all_10_mr: list[dict[str, str | int]] = []
    group_10_mr: list[dict[str, str | int]] = []

    player_chars_mr: dict[str, list[tuple[str, int]]] = {}
    display_mr_rank = 1
    previous_mr = 0
    streak = 0

    for i, (_, player_id, player_name, char_id, _, mr) in enumerate(mr_df.values):
        i += 1

        if mr != previous_mr:
            display_mr_rank = i
        else:
            streak += 1
            display_mr_rank = i - streak

        previous_mr = mr

        all_10_mr.append(
            {
                "class": fetch_mr_league_name(mr)["class"],
                "player_name": player_name,
                "player_id": player_id,
                "char_id": char_id,
                "value": mr,
                "rank": display_mr_rank,
                "league_name": fetch_mr_league_name(mr)["name"],
            }
        )

        if player_name not in player_chars_mr:
            player_chars_mr[player_name] = []

            group_10_mr.append(
                {
                    "class": fetch_mr_league_name(mr)["class"],
                    "player_name": player_name,
                    "player_id": player_id,
                    "char_id": char_id,
                    "value": mr,
                    "league_name": fetch_mr_league_name(mr)["name"],
                }
            )

    return (all_10_mr, group_10_mr)


def generate_lp_board(
    rank_df: pd.DataFrame,
) -> tuple[list[dict[str, str | int]], list[dict[str, str | int]]]:
    """Returns the sorted list for LP boards."""

    all_10_lp: list[dict[str, str | int]] = []
    group_10_lp: list[dict[str, str | int]] = []
    player_chars_lp: dict[str, bool] = {}

    display_lp_rank = 1
    previous_lp = 0
    streak = 0

    for i, (_, player_id, player_name, char_id, lp, _) in enumerate(rank_df.values):
        i += 1

        if lp != previous_lp:
            display_lp_rank = i
        else:
            streak += 1
            display_lp_rank = i - streak

        previous_lp = lp
        league = fetch_league_name(lp)
        all_10_lp.append(
            {
                "class": league["class"],
                "player_name": player_name,
                "player_id": player_id,
                "char_id": char_id,
                "value": lp,
                "rank": display_lp_rank,
                "league_name": league["name"],
            }
        )

        if player_name not in player_chars_lp:
            player_chars_lp[player_name] = True

            group_10_lp.append(
                {
                    "class": league["class"],
                    "player_name": player_name,
                    "player_id": player_id,
                    "char_id": char_id,
                    "value": lp,
                    "league_name": league["name"],
                }
            )

    return (all_10_lp, group_10_lp)


def generate_kudos_board(hs_df: pd.DataFrame) -> list[dict[str, str | int]]:
    """Returns the sorted list for the Kudos board."""

    kudos_leaders: list[dict[str, str | int]] = []

    top_kudos_df = hs_df.sort_values(by="total_kudos", ascending=False)

    for i, (_, player_id, player_name, total_kudos) in enumerate(top_kudos_df.values):
        class_name = "bottom" if i > 10 else ""
        class_name = class_name + " " + get_kudos_class(total_kudos)
        kudos_leaders.append(
            {
                "class": class_name,
                "player_name": player_name,
                "player_id": player_id,
                "value": total_kudos,
            }
        )

    return kudos_leaders


def get_list_of_dates():
    """Returns a list of dates the site has data for"""
    sql = """SELECT DISTINCT date FROM ranking ORDER BY date DESC;"""
    results = query_db(sql)
    dates_with_data = [x[0] for x in results] if results else []
    return dates_with_data


@dataclasses.dataclass
class MRPosition:
    """Class object for leaderboards"""

    rank: int
    date: str
    player_id: str
    player_name: str
    char_id: str
    lp: str
    mr: str


@bp.route("/", defaults={"date_req": ""})
@bp.route("/<string:date_req>")
def mr_leaderboard(date_req: str) -> str:
    """Displays the MR leaderboard."""
    date_list = get_list_of_dates()

    final_date_list = []

    for date in date_list:
        for phases in phase_dates.items():
            if phases[1][0] <= date <= phases[1][1]:
                final_date_list.append((date, phases[0]))

    split_date = date_req.split("-")
    req_datetime = datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")
    req_datetime = latest_stats_date()

    if len(split_date) == 3:
        y, m, d = split_date
        if len(y) == 4 and len(m) == 2 and len(d) == 2:
            req_datetime = (
                datetime.now(ZoneInfo("America/Los_Angeles"))
                .replace(
                    microsecond=0,
                    second=0,
                    minute=0,
                    hour=12,
                    year=int(y),
                    month=int(m),
                    day=int(d),
                )
                .strftime("%Y-%m-%d")
            )

    latest_mr_scores: str = (
        """SELECT ROW_NUMBER () OVER 
            ( ORDER BY r.mr DESC) rank, r.date, r.player_id, cm.player_name, r.char_id, r.lp, r.mr
            FROM ranking r
            INNER JOIN club_members cm ON cm.player_id = r.player_id
            WHERE date = ?
                AND mr > 0
                AND hidden = 0
            GROUP BY r.date, r.player_id, r.char_id;"""
    )

    mr_results = query_db(latest_mr_scores, args=(req_datetime,))
    mr_list = [MRPosition(*row) for row in mr_results] if mr_results else []

    for result in mr_list:
        result.char_id = charid_map[result.char_id]

    latest_lp_scores: str = (
        """SELECT ROW_NUMBER () OVER 
            ( ORDER BY r.lp DESC) rank, r.date, r.player_id, cm.player_name, r.char_id, r.lp, r.mr
            FROM ranking r
            INNER JOIN club_members cm ON cm.player_id = r.player_id
            WHERE date = ?
                AND mr > 0
                AND hidden = 0
            GROUP BY r.date, r.player_id, r.char_id;"""
    )

    lp_results = query_db(latest_lp_scores, args=(req_datetime,))
    lp_list = [MRPosition(*row) for row in lp_results] if lp_results else []

    for result in lp_list:
        result.char_id = charid_map[result.char_id]

    selected_date_index = date_list.index(req_datetime)

    prev_link = (
        date_list[selected_date_index + 1]
        if selected_date_index + 1 < len(date_list)
        else -1
    )
    next_link = date_list[selected_date_index - 1] if selected_date_index > 0 else -1

    return render_template(
        "leaderboards/mr_board.html.j2",
        date_list=final_date_list,
        date_selected=req_datetime,
        mr_list=mr_list,
        lp_list=lp_list,
        prev_link=prev_link,
        next_link=next_link,
    )


def leaderboards(date_req: str) -> str:
    """Displays MR/LP/Kudos leaderboards and stats for the club."""

    # hit db to get latest data point
    latest_data_date_sql = """SELECT date, download_complete, parsing_complete
                            FROM last_update
                            WHERE download_complete = 1 AND parsing_complete = 1
                            ORDER BY date DESC
                            LIMIT 1;"""

    if not date_req:
        try:
            with sqlite3.connect("cfn-stats.db") as conn:
                cursor = conn.cursor()
                cursor.execute(latest_data_date_sql)
                results = cursor.fetchone()
                if results[0]:
                    date_req = results[0]
        except sqlite3.Error as e:
            print(e)

    split_date = date_req.split("-")
    req_datetime = datetime.now(ZoneInfo("America/Los_Angeles"))
    if len(split_date) == 3:
        y, m, d = split_date
        if len(y) == 4 and len(m) == 2 and len(d) == 2:
            yint = int(y)
            mint = int(m)
            dint = int(d)
            req_datetime = datetime.now(ZoneInfo("America/Los_Angeles")).replace(
                microsecond=0,
                second=0,
                minute=0,
                hour=12,
                year=yint,
                month=mint,
                day=dint,
            )

    top_10_boards, top_10_grouped = generate_leaderboards(req_datetime)

    awards_list = generate_awards()

    date_list = get_list_of_dates()

    final_list = []

    for date in date_list:
        for phases in phase_dates.items():
            if phases[1][0] <= date <= phases[1][1]:
                final_list.append((date, phases[0]))

    return render_template(
        "leaderboards/club_leaderboards.html.j2",
        top_10_boards=top_10_boards,
        top_10_grouped=top_10_grouped,
        awards_list=awards_list,
        date_selected=req_datetime.strftime("%Y-%m-%d"),
        date_list=final_list,
    )
