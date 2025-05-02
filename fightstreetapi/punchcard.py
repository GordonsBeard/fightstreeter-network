"""generate the player's punchcard"""

from dataclasses import field

from apiflask import APIBlueprint, abort
from apiflask.validators import Length, OneOf
from flask_cors import CORS
from marshmallow_dataclass import dataclass

from constants import charid_map

from .db import dates_with_data, query_db
from .player import CharacterRanking

bp = APIBlueprint("punchcard", __name__, url_prefix="/punchcard")
CORS(bp)


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
    ranked_changes: dict | None


@bp.get("/")
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

    hs_results = query_db(punchard_hs_req_sql, (query_data.player_id, query_data.date))

    ranking_req_sql = """SELECT * FROM ranking
        WHERE date IN (SELECT DISTINCT date FROM ranking WHERE date <= ? ORDER BY date DESC LIMIT 2)
            AND player_id = ?
        ORDER BY date DESC;
        """

    ranking_results = query_db(ranking_req_sql, (query_data.date, query_data.player_id))

    if not hs_results or not ranking_results or len(hs_results) != 2:
        abort(404)

    hs_today, hs_yesterday = hs_results[0], hs_results[1]
    yesterday_total_matches = (
        (hs_today["hub_matches"] - hs_yesterday["hub_matches"])
        + (hs_today["ranked_matches"] - hs_yesterday["ranked_matches"])
        + (hs_today["casual_matches"] - hs_yesterday["casual_matches"])
        + (hs_today["custom_matches"] - hs_yesterday["custom_matches"])
    )
    yesterday_total_time = (
        (hs_today["hub_time"] - hs_yesterday["hub_time"])
        + (hs_today["ranked_time"] - hs_yesterday["ranked_time"])
        + (hs_today["casual_time"] - hs_yesterday["casual_time"])
        + (hs_today["extreme_time"] - hs_yesterday["extreme_time"])
        + (hs_today["versus_time"] - hs_yesterday["versus_time"])
        + (hs_today["practice_time"] - hs_yesterday["practice_time"])
        + (hs_today["arcade_time"] - hs_yesterday["arcade_time"])
        + (hs_today["wt_time"] - hs_yesterday["wt_time"])
    )

    list_of_ranks: list[CharacterRanking] = [
        CharacterRanking(**row) for row in ranking_results
    ]

    char_ranks = {}

    if len({row.date for row in list_of_ranks}) > 1:
        yesterday_ranks = {}
        today_ranks = {}
        ## Edgecase:
        ## If you have played the last day of Phase n but have not played during Phase n+1
        ## then the below line is going to fail as there is only one day you will get ranks
        ## from the characters you have played this PHASE.
        yesterday_date, today_date = {row.date for row in list_of_ranks}
        char_ids = {char.char_id for char in list_of_ranks}

        for rank in list_of_ranks:
            if rank.date == yesterday_date:
                if rank.char_id not in yesterday_ranks:
                    yesterday_ranks[rank.char_id] = {"lp": rank.lp, "mr": rank.mr}
            if rank.date == today_date:
                if rank.char_id not in today_ranks:
                    today_ranks[rank.char_id] = {"lp": rank.lp, "mr": rank.mr}

        for character_id in char_ids:
            char_name = charid_map[character_id]
            if char_name not in char_ranks:
                char_ranks[char_name] = {"lp": 0, "mr": 0}
            char_ranks[char_name]["lp"] = (
                today_ranks[character_id]["lp"] - yesterday_ranks[character_id]["lp"]
            )
            char_ranks[char_name]["mr"] = (
                today_ranks[character_id]["mr"] - yesterday_ranks[character_id]["mr"]
            )

    punchcard = PunchCard(
        date=hs_today["date"],
        prev_date=hs_yesterday["date"],
        player_id=query_data.player_id,
        player_name=hs_today["player_name"],
        selected_char=charid_map[hs_today["selected_char"]],
        total_matches=yesterday_total_matches,
        hub_matches=hs_today["hub_matches"] - hs_yesterday["hub_matches"],
        ranked_matches=hs_today["ranked_matches"] - hs_yesterday["ranked_matches"],
        casual_matches=hs_today["casual_matches"] - hs_yesterday["casual_matches"],
        custom_matches=hs_today["custom_matches"] - hs_yesterday["custom_matches"],
        total_time=yesterday_total_time,
        hub_time=hs_today["hub_time"] - hs_yesterday["hub_time"],
        ranked_time=hs_today["ranked_time"] - hs_yesterday["ranked_time"],
        casual_time=hs_today["casual_time"] - hs_yesterday["casual_time"],
        extreme_time=hs_today["extreme_time"] - hs_yesterday["extreme_time"],
        custom_time=hs_today["custom_time"] - hs_yesterday["custom_time"],
        versus_time=hs_today["versus_time"] - hs_yesterday["versus_time"],
        practice_time=hs_today["practice_time"] - hs_yesterday["practice_time"],
        arcade_time=hs_today["arcade_time"] - hs_yesterday["arcade_time"],
        wt_time=hs_today["wt_time"] - hs_yesterday["wt_time"],
        kudos_gained=hs_today["total_kudos"] - hs_yesterday["total_kudos"],
        thumbs_gained=hs_today["thumbs"] - hs_yesterday["thumbs"],
        ranked_changes=char_ranks,
    )

    return punchcard
