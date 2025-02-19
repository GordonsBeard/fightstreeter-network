"""funny animals roster/character select"""

import dataclasses

from flask import Blueprint, render_template

from fightstreeter import db

bp = Blueprint("roster", __name__, url_prefix="/roster")


@dataclasses.dataclass
class Player:
    player_name: str
    player_id: str


@bp.route("/")
def roster() -> str:
    all_members_sql = """SELECT player_name, player_id FROM club_members;"""
    all_members = db.query_db(all_members_sql)
    all_members_list = [Player(*row) for row in all_members]  # type: ignore

    return render_template(
        "roster/roster.html.j2",
        member_list=all_members_list,
    )
