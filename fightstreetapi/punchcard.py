"""generate the player's punchcard"""

from dataclasses import field

from apiflask import APIBlueprint, abort
from apiflask.validators import Length, OneOf
from marshmallow_dataclass import dataclass

from constants import charid_map

from .db import dates_with_data, query_db

bp = APIBlueprint("punchcard", __name__, url_prefix="/punchcard")


@dataclass
class PunchCardRequest:
    """Request schema for player punchcard"""

    player_id: str = field(
        metadata={
            "required": True,
            "validate": Length(min=10, max=10),
            "metadata": {"example": "3425126856"},
        }
    )
    date: str = field(
        metadata={
            "required": True,
            "validate": OneOf(dates_with_data()),
            "metadata": {"example": "2025-04-17"},
        }
    )


@dataclass
class PunchCard:
    """Player's punchcard for a date. Time in seconds."""

    date: str
    prev_date: str
    player_id: str
    player_name: str
    selected_char: str
    total_matches: int
    hub_matches: int
    ranked_matches: int
    casual_matches: int
    custom_matches: int
    total_time: int
    hub_time: int
    ranked_time: int
    casual_time: int
    custom_time: int
    extreme_time: int
    versus_time: int
    practice_time: int
    arcade_time: int
    wt_time: int
    kudos_gained: int
    thumbs_gained: int


@bp.post("/")
@bp.input(PunchCardRequest.Schema, location="query")  # type: ignore # pylint: disable=maybe-no-member
@bp.output(PunchCard.Schema)  # type: ignore # pylint: disable=maybe-no-member
@bp.doc(
    summary="Generate punchcard",
    description="Gives you a summary of all the things you did on this date in SF6.",
)
def generate_punchcard_route(query_data: PunchCardRequest) -> PunchCard:
    """Generates the player's punchchard"""

    punchard_hs_req_sql = """SELECT
        date,
        hs.player_name,
        hs.player_id,
        selected_char as selected_char,
        lp as selected_lp,
        mr as selected_mr,
        hub_matches,
        ranked_matches,
        casual_matches,
        custom_matches,
        hub_time,
        ranked_time,
        casual_time,
        custom_time,
        extreme_time,
        versus_time,
        practice_time,
        arcade_time,
        wt_time,
        total_kudos,
        thumbs
        FROM historic_stats hs
        WHERE hs.player_id = ?
        AND date <= ? ORDER BY date DESC LIMIT 2;"""

    results = query_db(punchard_hs_req_sql, (query_data.player_id, query_data.date))

    if not results:
        abort(404)

    if len(results) != 2:
        abort(404)

    today, yesterday = results[0], results[1]
    yesterday_total_matches = (
        (today["hub_matches"] - yesterday["hub_matches"])
        + (today["ranked_matches"] - yesterday["ranked_matches"])
        + (today["casual_matches"] - yesterday["casual_matches"])
        + (today["custom_matches"] - yesterday["custom_matches"])
    )
    yesterday_total_time = (
        (today["hub_time"] - yesterday["hub_time"])
        + (today["ranked_time"] - yesterday["ranked_time"])
        + (today["casual_time"] - yesterday["casual_time"])
        + (today["extreme_time"] - yesterday["extreme_time"])
        + (today["versus_time"] - yesterday["versus_time"])
        + (today["practice_time"] - yesterday["practice_time"])
        + (today["arcade_time"] - yesterday["arcade_time"])
        + (today["wt_time"] - yesterday["wt_time"])
    )

    punchcard = PunchCard(
        date=today["date"],
        prev_date=yesterday["date"],
        player_id=query_data.player_id,
        player_name=today["player_name"],
        selected_char=charid_map[today["selected_char"]],
        total_matches=yesterday_total_matches,
        hub_matches=today["hub_matches"] - yesterday["hub_matches"],
        ranked_matches=today["ranked_matches"] - yesterday["ranked_matches"],
        casual_matches=today["casual_matches"] - yesterday["casual_matches"],
        custom_matches=today["custom_matches"] - yesterday["custom_matches"],
        total_time=yesterday_total_time,
        hub_time=today["hub_time"] - yesterday["hub_time"],
        ranked_time=today["ranked_time"] - yesterday["ranked_time"],
        casual_time=today["casual_time"] - yesterday["casual_time"],
        extreme_time=today["extreme_time"] - yesterday["extreme_time"],
        custom_time=today["custom_time"] - yesterday["custom_time"],
        versus_time=today["versus_time"] - yesterday["versus_time"],
        practice_time=today["practice_time"] - yesterday["practice_time"],
        arcade_time=today["arcade_time"] - yesterday["arcade_time"],
        wt_time=today["wt_time"] - yesterday["wt_time"],
        kudos_gained=today["total_kudos"] - yesterday["total_kudos"],
        thumbs_gained=today["thumbs"] - yesterday["thumbs"],
    )

    return punchcard
