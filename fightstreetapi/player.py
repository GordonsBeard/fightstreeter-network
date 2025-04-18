"""player stats"""

from apiflask import APIBlueprint, abort
from marshmallow_dataclass import dataclass

from constants import charid_map

from . import db

bp = APIBlueprint("player", __name__, url_prefix="/player")


@dataclass
class PlayerProfile:  # pylint: disable=too-many-instance-attributes
    """Player's profile schema"""

    player_name: str
    player_id: str
    date_joined: str
    selected_character: str
    selected_lp: int
    selected_mr: int
    hub_matches: int
    ranked_matches: int
    casual_matches: int
    custom_matches: int
    hub_time: int
    ranked_time: int
    casual_time: int
    custom_time: int
    extreme_time: int
    versus_time: int
    practice_time: int
    arcade_time: int
    wt_time: int
    total_kudos: int
    thumbs: int
    last_played: str
    profile_tagline: str
    title_text: str
    title_plate: str


@dataclass
class Character:
    """Individual character LP/MR stats"""

    char_id: str
    lp: str
    mr: str


@bp.get("/id/<string:req_player>")
@bp.output(PlayerProfile.Schema)  # type: ignore # pylint: disable=maybe-no-member
def player_all_characters(req_player, req_date=db.latest_stats_date()) -> PlayerProfile:
    """Player overview/profile via player_id"""

    # Support username or id, start with username
    player_profile_sql: str = (
        """SELECT hs.player_name, hs.player_id, joined_at date_joined, selected_char as selected_character,
                lp as selected_lp, mr as selected_mr, hub_matches, ranked_matches, casual_matches,
                custom_matches, hub_time, ranked_time, casual_time, custom_time, extreme_time,
                versus_time, practice_time, arcade_time, wt_time, total_kudos, thumbs, last_played,
                profile_tagline, title_text, title_plate
            FROM historic_stats hs
            INNER JOIN club_members cm ON cm.player_id = hs.player_id
            WHERE hs.date = ? AND hs.player_id = ?"""
    )

    result = db.query_db(player_profile_sql, (req_date, req_player), one=True)

    if not result:
        abort(404)

    player_overview = PlayerProfile(*result)
    player_overview.selected_character = charid_map[player_overview.selected_character]

    return player_overview


@bp.get("/id/<string:req_player>/characters")
@bp.output(Character.Schema(many=True))  # type: ignore # pylint: disable=maybe-no-member
@bp.doc(
    summary="Player's characters' stats",
    description="Returns the LP/MR for every character played by a given user.",
)
def player_characters(req_player) -> list[Character]:
    """Stats on every character played by a given user"""

    # Support username or id, start with username
    player_characters_sql: str = (
        """SELECT char_id, lp, mr
            FROM ranking
            WHERE player_id = ? AND date = ?;"""
    )

    result = db.query_db(player_characters_sql, (req_player, db.latest_stats_date()))

    if not result:
        abort(404)

    player_overview = [Character(**row) for row in result]

    for char in player_overview:
        char.char_id = charid_map[char.char_id]

    return player_overview
