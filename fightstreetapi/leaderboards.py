"""Generates the LP/MR/Kudos leaderboards"""

from dataclasses import field
from datetime import datetime
from zoneinfo import ZoneInfo

from apiflask import APIBlueprint
from apiflask.validators import OneOf
from flask_cors import CORS
from marshmallow_dataclass import dataclass

from constants import charid_map

from . import db

bp = APIBlueprint("leaderboards", __name__, url_prefix="/leaderboards")
CORS(bp, origins="localhost")

boards = ["mr-all", "lp-all"]


@dataclass
class LeaderboardPlayer:
    """Individual player on a leaderboard."""

    player_name: str
    player_id: str
    character: str
    value: str


@dataclass
class Leaderboard:
    """Leaderboard schema."""

    name: str
    desc: str
    date: str
    players: list[LeaderboardPlayer]


@dataclass
class LeaderboardRequest:
    """Request schema for getting a leaderboard at a point in time"""

    date: str = field(
        metadata={
            "required": True,
            "validate": OneOf(db.dates_with_data()),
            "metadata": {"example": "2025-04-17"},
        }
    )

    board: str = field(
        metadata={
            "required": True,
            "validate": OneOf(boards),
            "metadata": {"example": "mr-all"},
        }
    )


def get_leaderboard(col_name: str, date_req: str) -> list[LeaderboardPlayer]:
    """Function to retrieve simple leaderboard for LP or MR."""
    split_date = date_req.split("-")
    y, m, d = split_date

    req_date = (
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
        f"""SELECT r.player_id, cm.player_name, r.char_id as character, {col_name} as value
            FROM ranking r
            INNER JOIN club_members cm ON cm.player_id = r.player_id
            WHERE date = ?
                AND mr > 0
                AND hidden = 0
            ORDER BY value DESC;"""
    )

    results = db.query_db(
        latest_mr_scores,
        args=(req_date,),
    )
    player_list = [LeaderboardPlayer(**row) for row in results] if results else []

    for result in player_list:
        result.character = charid_map[result.character]

    return player_list


@bp.get("/")
@bp.input(LeaderboardRequest.Schema, location="query")  # type: ignore #pylint: disable=maybe-no-member
@bp.output(Leaderboard.Schema)  # type: ignore #pylint: disable=maybe-no-member
@bp.doc(
    summary="Retrieve leaderboards",
    description="Returns the requested leaderboard. Default sort high mr/lp to low.",
)
def mr_leaderboard(query_data: LeaderboardRequest) -> Leaderboard:
    """Displays the MR leaderboard."""
    date = query_data.date if query_data else db.latest_stats_date()
    player_list = (
        get_leaderboard("r.mr", date)
        if query_data.board == "mr-all"
        else get_leaderboard("r.lp", date)
    )
    name = (
        "Master Rate (all)" if query_data.board == "mr-all" else "League Points (all)"
    )
    desc = (
        "MR for characters across all players."
        if query_data.board == "mr-all"
        else "LP for characters across all players."
    )

    return Leaderboard(
        name=name,
        desc=desc,
        players=player_list,
        date=date,
    )
