"""fightstreetapi - backend for fightstreeter.com"""

import dataclasses

from apiflask import APIBlueprint, Schema
from apiflask.fields import String

from . import db

bp = APIBlueprint("roster", __name__, url_prefix="/roster")


@dataclasses.dataclass
class Player:
    """Class object for a club member"""

    date: str
    player_name: str
    player_id: str
    last_played: str
    lp: str


class PlayerSchema(Schema):
    """APIFlask output class"""

    player_name = String()
    player_id = String()
    last_played = String()


def generate_member_list() -> list[Player]:
    """Returns the list of club players with sorting"""
    all_members_sql = """SELECT hs.date, hs.player_name, hs.player_id, hs.last_played, hs.lp
        FROM historic_stats hs
        LEFT JOIN club_members cm ON cm.player_id = hs.player_id
        WHERE hs.date = ? AND cm.hidden = 0
        ORDER BY hs.last_played DESC, hs.player_name;"""

    all_members = db.query_db(all_members_sql, (db.latest_stats_date(),))
    all_members_list = [Player(**row) for row in all_members] if all_members else []

    return all_members_list


@bp.get("/")
@bp.output(PlayerSchema(many=True))
@bp.doc(summary="Get club members", description="Returns a list of every club member.")
def get_club_roster():
    all_members_list = generate_member_list()
    schema = PlayerSchema(many=True)
    result = schema.dump(all_members_list)
    return result
