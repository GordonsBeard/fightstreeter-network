"""Generates the LP/MR/Kudos leaderboards"""

from datetime import datetime
from zoneinfo import ZoneInfo

from apiflask import APIBlueprint
from marshmallow_dataclass import dataclass

from constants import charid_map

from . import db

bp = APIBlueprint("leaderboards", __name__, url_prefix="/leaderboards")


def get_list_of_dates() -> list[str]:
    """Returns a list of dates the site has data for"""
    sql = """SELECT DISTINCT date FROM ranking ORDER BY date DESC;"""
    results = db.query_db(sql)
    dates_with_data: list[str] = [x[0] for x in results] if results else []
    return dates_with_data


@dataclass
class LeaderboardPlayer:
    """Individual player on a leaderboard."""

    rank: int
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
        f"""SELECT ROW_NUMBER () OVER ( ORDER BY r.mr DESC) rank,
            r.player_id, cm.player_name, r.char_id as character, {col_name} as value
            FROM ranking r
            INNER JOIN club_members cm ON cm.player_id = r.player_id
            WHERE date = ?
                AND mr > 0
                AND hidden = 0
            GROUP BY r.player_id, r.char_id;"""
    )

    results = db.query_db(
        latest_mr_scores,
        args=(req_date,),
    )
    player_list = [LeaderboardPlayer(**row) for row in results] if results else []

    for result in player_list:
        result.character = charid_map[result.character]

    return player_list


@bp.get("/master-rate/")
@bp.get("/master-rate/<string:date_req>")
@bp.output(Leaderboard.Schema)  # type: ignore # pylint: disable=no-member
@bp.doc(
    summary="MR Leaderboard (all)",
    description="Returns the MR obtained for every player's character(s). Sorted high to low.",
)
def mr_leaderboard(date_req: str = db.latest_stats_date()) -> Leaderboard:
    """Displays the MR leaderboard."""
    player_list = get_leaderboard("r.mr", date_req)

    return Leaderboard(
        name="Master Rate (all)",
        desc="MR for characters across all players.",
        players=player_list,
        date=date_req,
    )


@bp.get("/league-points/")
@bp.get("/league-points/<string:date_req>")
@bp.output(Leaderboard.Schema)  # type: ignore # pylint: disable=no-member
@bp.doc(
    summary="LP Leaderboard (all)",
    description="Returns the League Points obtained for every player's character(s). Sorted high to low.",
)
def lp_leaderboard(date_req: str = db.latest_stats_date()) -> Leaderboard:
    """Displays the LP leaderboard."""
    player_list = get_leaderboard("r.lp", date_req)

    return Leaderboard(
        name="League Points (all)",
        desc="LP for characters across all players.",
        players=player_list,
        date=date_req,
    )
