"""player stats"""

import random
import pandas as pd
import plotly.graph_objects as go
from dataclasses import field
from datetime import datetime, timedelta

from apiflask import APIBlueprint, abort
from apiflask.validators import Length, OneOf
from flask_cors import CORS
from marshmallow_dataclass import dataclass

from constants import charid_map, phase_dates

from .db import query_db

bp = APIBlueprint("player", __name__, url_prefix="/player")
CORS(bp)


@dataclass
class PlayerHistoricStats:  # pylint: disable=too-many-instance-attributes
    """Player's profile schema"""

    date: str
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
class DateRangeRequest:
    """Historic stats for a player between two given dates"""

    player_id: str = field(
        metadata={
            "required": True,
            "validate": Length(min=10, max=10),
            "metadata": {"example": "3425126856"},
        }
    )
    date_start: str = field(
        metadata={
            "required": False,
            "metadata": {"example": "2025-04-01"},
        }
    )

    date_end: str = field(
        metadata={
            "required": False,
            "metadata": {"example": "2025-04-17"},
        }
    )

    phase: int = field(
        metadata={
            "required": False,
            "metadata": {"example": 6},
        }
    )

    fetch_range: bool = field(
        metadata={
            "required": True,
            "validate": OneOf([True, False]),
            "metadata": {"example": True},
        }
    )


@dataclass
class CharacterRanking:
    """Individual character LP/MR stats"""

    date: str
    phase: int
    player_id: str
    char_id: str
    lp: int
    mr: int


def player_overview_snapshot(query_data: DateRangeRequest) -> list[PlayerHistoricStats]:
    """Internal call to get some historic_stats data between two dates"""
    if query_data.date_end < query_data.date_start:
        query_data.date_end, query_data.date_start = (
            query_data.date_start,
            query_data.date_end,
        )

    range_sql = (
        """(hs.date BETWEEN ? AND ?)"""
        if query_data.fetch_range
        else """(hs.date = ? OR hs.date = ?)"""
    )

    # Support username or id, start with username
    historic_stats_daterange_sql: str = (
        f"""SELECT date, hs.player_name, hs.player_id, joined_at date_joined, selected_char as selected_character,
                lp as selected_lp, mr as selected_mr, hub_matches, ranked_matches, casual_matches,
                custom_matches, hub_time, ranked_time, casual_time, custom_time, extreme_time,
                versus_time, practice_time, arcade_time, wt_time, total_kudos, thumbs, last_played,
                profile_tagline, title_text, title_plate
            FROM historic_stats hs
            INNER JOIN club_members cm ON cm.player_id = hs.player_id
            WHERE hs.player_id = ? AND {range_sql}"""
    )

    results = query_db(
        historic_stats_daterange_sql,
        (query_data.player_id, query_data.date_start, query_data.date_end),
    )

    if not results:
        abort(404)

    player_overview = [PlayerHistoricStats(**result) for result in results]
    for historicstats_entry in player_overview:
        historicstats_entry.selected_character = charid_map[
            historicstats_entry.selected_character
        ]

    return player_overview


def player_ranking_snapshot(query_data) -> list[CharacterRanking]:
    """Internal call to get ranking information every character played by a user this phase."""
    if not query_data.date_end and not query_data.date_start and not query_data.phase:
        abort(404)

    if query_data.phase:
        player_characters_sql: str = (
            """SELECT date, phase, player_id, char_id, lp, mr
            FROM ranking
            WHERE phase = ? AND player_id = ?
            ORDER BY date ASC;"""
        )
        result = query_db(
            player_characters_sql,
            (query_data.phase, query_data.player_id),
        )
    else:
        if query_data.date_end < query_data.date_start:
            query_data.date_end, query_data.date_start = (
                query_data.date_start,
                query_data.date_end,
            )

        player_characters_sql: str = (
            (
                """SELECT date, phase, player_id, char_id, lp, mr
                FROM ranking
                WHERE date BETWEEN ? AND ? AND player_id = ?;"""
            )
            if query_data.fetch_range
            else (
                """SELECT date, phase, char_id, lp, mr
                FROM ranking
                WHERE (date = ? OR date = ?) AND player_id = ?;"""
            )
        )

        result = query_db(
            player_characters_sql,
            (query_data.date_start, query_data.date_end, query_data.player_id),
        )

    if not result:
        abort(404)

    list_of_char_ranks = [CharacterRanking(**row) for row in result]

    for character_rank in list_of_char_ranks:
        character_rank.char_id = charid_map[character_rank.char_id]

    return list_of_char_ranks


@bp.get("/overview")
@bp.input(DateRangeRequest.Schema, location="query")  # type: ignore # pylint: disable=maybe-no-member
@bp.output(PlayerHistoricStats.Schema(many=True))  # type: ignore # pylint: disable=maybe-no-member
@bp.doc(
    summary="Player's overview snapshot",
    description="Returns the historic_stats row containing the summary of stats for the player for each given date.",
)
def player_overview_snapshot_route(
    query_data: DateRangeRequest,
) -> list[PlayerHistoricStats]:
    """Player's historic_stats snapshot between two dates."""

    player_overview = player_overview_snapshot(query_data)

    return player_overview


@bp.get("/ranking")
@bp.input(DateRangeRequest.Schema, location="query")  # type: ignore # pylint: disable=maybe-no-member
@bp.output(CharacterRanking.Schema(many=True))  # type: ignore # pylint: disable=maybe-no-member
@bp.doc(
    summary="Player's ranking snapshot",
    description="Returns the LP/MR for every character played by a given user for the given date.",
)
def player_ranking_snapshot_route(query_data) -> list[CharacterRanking]:
    """MR/LP stats on every character played by a given user"""

    player_rankings = player_ranking_snapshot(query_data)

    return player_rankings


@dataclass
class CharGraphs:
    all_dates: list[str]
    characters: dict[str, dict[str, list[str]]]


@bp.get("/ranking/graph")
@bp.input(DateRangeRequest.Schema, location="query")  # type: ignore # pylint: disable=maybe-no-member
@bp.doc(
    summary="Player's ranking graph",
    description="Returns a list of player rank dictionaries for building a plotly graph for a phase.",
)
def player_ranking_graph(query_data: DateRangeRequest):
    """Building MR/LP data for plotly graph in phython instead of on client"""
    if not query_data.phase or query_data.phase < 2:
        abort(404)

    phase = query_data.phase
    phase_start_date = datetime.strptime(phase_dates[phase][0], "%Y-%m-%d")
    phase_end_date = datetime.strptime(phase_dates[phase][1], "%Y-%m-%d")
    date_range = []
    while phase_start_date <= phase_end_date:
        date_range.append(phase_start_date.strftime("%Y-%m-%d"))
        phase_start_date += timedelta(days=1)

    player_rankings = player_ranking_snapshot(query_data)

    characters = {}

    for ranking in player_rankings:
        if ranking.char_id not in characters:
            characters[ranking.char_id] = {"dates": [], "lp": [], "mr": []}
        characters[ranking.char_id]["dates"].append(ranking.date)
        characters[ranking.char_id]["lp"].append(ranking.lp)
        characters[ranking.char_id]["mr"].append(ranking.mr if ranking.mr > 0 else None)

    character_graphs = CharGraphs(date_range, characters)

    dates = character_graphs.all_dates

    lp_fig = go.Figure()
    mr_fig = go.Figure()

    for char in character_graphs.characters:
        character_lp = character_graphs.characters[char]["lp"]
        character_mr = character_graphs.characters[char]["mr"]
        lp_fig.add_trace(go.Scatter(x=dates, y=character_lp, name=char, line=dict(width=4), showlegend=True))
        mr_fig.add_trace(go.Scatter(x=dates, y=character_mr, name=char, line=dict(width=4), showlegend=True))


    for fig in (lp_fig, mr_fig):
        fig.update_layout(
            template="plotly_dark", 
            yaxis_tickformat=".0f",
            
        )

    lp_graph = lp_fig.to_plotly_json()
    mr_graph = mr_fig.to_plotly_json()

    return {"lp": lp_graph, "mr": mr_graph}