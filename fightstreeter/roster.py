"""funny animals roster/character select"""

import dataclasses

from flask import Blueprint, render_template

from fightstreeter import db

from .awards import generate_awards

bp = Blueprint("roster", __name__, url_prefix="/roster")


@dataclasses.dataclass
class Player:
    """Class object for a club member"""

    date: str
    player_name: str
    player_id: str
    last_played: str


def generate_member_list() -> list[Player]:
    """Returns the list of club players with sorting"""
    all_members_sql = """SELECT hs.date, hs.player_name, hs.player_id, hs.last_played
        FROM historic_stats hs
        LEFT JOIN club_members cm ON cm.player_id = hs.player_id
        WHERE hs.date = ? AND cm.hidden = 0
        ORDER BY hs.last_played DESC, hs.player_name;"""

    all_members = db.query_db(all_members_sql, (db.latest_stats_date(),))
    all_members_list = [Player(*row) for row in all_members] if all_members else []

    return all_members_list


@bp.route("/")
def club_overview() -> str:
    """Default homepage for the roster"""
    return render_template(
        "roster/roster.html.j2",
        member_list=generate_member_list(),
        latest_update=db.latest_stats_date(),
        awards_list=generate_awards(),
    )
