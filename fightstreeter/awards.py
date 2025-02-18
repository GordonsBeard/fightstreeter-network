"""Generate the awards for today."""

import random
import sqlite3

import pandas as pd

from constants import charid_map


def generate_awards() -> list[dict[str, str]]:
    """Returns the list of awards."""

    awards_list: list[dict[str, str]] = []

    conn: sqlite3.Connection = sqlite3.connect("cfn-stats.db")

    historic_stats_sql: str = (
        """SELECT *
        FROM historic_stats hs
        WHERE date = (SELECT MAX(date) FROM historic_stats)
        GROUP BY date, player_id, selected_char
        ORDER BY date DESC"""
    )

    latest_lp_scores: str = (
        """SELECT r.date, r.player_id, cm.player_name, r.char_id, r.lp, r.mr
        FROM ranking r
        INNER JOIN club_members cm ON cm.player_id = r.player_id
        WHERE date = (SELECT MAX(date) FROM ranking)
        GROUP BY r.date, r.player_id, r.char_id;"""
    )

    inactive_player_scores: str = (
        """SELECT hs.date, hs.player_id, hs.player_name, hs.selected_char as char_id, hs.lp, hs.mr
        FROM historic_stats hs
        WHERE date = (SELECT MAX(date) FROM historic_stats)
        GROUP BY hs.date, hs.player_id, char_id;"""
    )

    hs_df: pd.DataFrame = pd.read_sql_query(historic_stats_sql, conn)
    hs_df["selected_char"] = hs_df["selected_char"].replace(charid_map)

    # ranking table gets us the ranks from this phase
    rank_df: pd.DataFrame = pd.read_sql_query(latest_lp_scores, conn)
    rank_df["char_id"] = rank_df["char_id"].replace(charid_map)
    rank_df["date"] = pd.to_datetime(rank_df["date"], format="ISO8601")

    # historic stats table gets us the ranks of every player's current char (all phases)
    inactive_df: pd.DataFrame = pd.read_sql_query(inactive_player_scores, conn)
    inactive_df["char_id"] = inactive_df["char_id"].replace(charid_map)
    inactive_df["date"] = pd.to_datetime(inactive_df["date"], format="ISO8601")
    inactive_df = inactive_df[inactive_df["lp"] != -1]

    # combine the two ranking tables to get a complete list of everyone's lp/mr
    rank_df = pd.concat([inactive_df, rank_df]).drop_duplicates().reset_index(drop=True)

    conn.close()

    if len(hs_df.values) == 0:
        return awards_list

    basic_awards = generate_basic_awards(hs_df)
    awards_list += basic_awards

    char_awards = generate_character_awards(hs_df, rank_df)
    awards_list += char_awards

    return awards_list


def generate_character_awards(
    hs_df: pd.DataFrame, rank_df: pd.DataFrame
) -> list[dict[str, str]]:
    """Generate awards based on character usage."""

    awards_list: list[dict[str, str]] = []

    # Most Popular Selected
    pop_df = hs_df[["selected_char"]]
    char_name = pop_df.value_counts().to_frame().idxmax().item()[0]
    times_used = pop_df.value_counts().to_frame().max().item()
    awards_list.append(
        {
            "class": "pop-char",
            "name": "Most Popular",
            "player_name": char_name,
            "player_id": "",
            "value": f"Currently played by {times_used} people",
        }
    )

    # Least Popular Character
    # this one might disappear relatively soon, consider a new way of measuring this
    used_char_list = rank_df["char_id"].drop_duplicates().to_list()
    all_char_list = list(charid_map.values())

    unused_chars = [
        char for char in all_char_list if char not in used_char_list and char.isalpha()
    ]

    if len(unused_chars) == 1:
        awards_list.append(
            {
                "class": "unpop-char",
                "name": "Needs Represendation",
                "player_name": unused_chars[0],
                "player_id": "",
                "value": "Played by nobody in ranked...",
            }
        )

    return awards_list


def generate_basic_awards(hs_df: pd.DataFrame) -> list[dict[str, str]]:
    """Returns the list of basic (non-calculated) awards."""

    awards_list: list[dict[str, str]] = []

    bhub_matches_row = hs_df[hs_df["hub_matches"] == hs_df["hub_matches"].max()]
    awards_list.append(
        {
            "class": "hub-matches",
            "name": "Hub Monster",
            "player_name": bhub_matches_row["player_name"].item(),
            "player_id": bhub_matches_row["player_id"].item(),
            "value": f"{bhub_matches_row['hub_matches'].item():,} hub matches",
        }
    )

    custom_matches_row = hs_df[hs_df["custom_matches"] == hs_df["custom_matches"].max()]
    awards_list.append(
        {
            "class": "custom-matches",
            "name": "The V.I.P.",
            "player_name": custom_matches_row["player_name"].item(),
            "player_id": custom_matches_row["player_id"].item(),
            "value": f"{custom_matches_row['custom_matches'].item():,} custom room matches",
        }
    )

    ranked_matches_row = hs_df[hs_df["ranked_matches"] == hs_df["ranked_matches"].max()]
    awards_list.append(
        {
            "class": "ranked-matches",
            "name": "League Regular",
            "player_name": ranked_matches_row["player_name"].item(),
            "player_id": ranked_matches_row["player_id"].item(),
            "value": f"{ranked_matches_row['ranked_matches'].item():,} ranked matches",
        }
    )

    casual_matches_row = hs_df[hs_df["casual_matches"] == hs_df["casual_matches"].max()]
    awards_list.append(
        {
            "class": "casual-matches",
            "name": "Casual Matches",
            "player_name": casual_matches_row["player_name"].item(),
            "player_id": casual_matches_row["player_id"].item(),
            "value": f"{casual_matches_row['ranked_matches'].item():,} casual matches",
        }
    )

    extreme_time_row = hs_df[hs_df["extreme_time"] == hs_df["extreme_time"].max()]
    awards_list.append(
        {
            "class": "extreme-time",
            "name": "Extreme Matches",
            "player_name": extreme_time_row["player_name"].item(),
            "player_id": extreme_time_row["player_id"].item(),
            "value": f"{extreme_time_row['extreme_time'].item()/60:.0f} minutes of Extreme Battles",
        }
    )
    geight_time = hs_df[hs_df["player_id"] == "2251667984"]["versus_time"].item()
    dos_time = hs_df[hs_df["player_id"] == "2531364579"]["versus_time"].item()
    newest_date = hs_df[hs_df["date"] == hs_df["date"].max()]["date"].values[0]

    dos_geight_name = "Geight & Dos" if random.random() > 0.5 else "Dos & Geight"

    geight_n_dos = {
        "date": newest_date,
        "player_id": "1234567890",
        "player_name": dos_geight_name,
        "versus_time": dos_time + geight_time,
    }

    hs_df = pd.concat([hs_df, pd.DataFrame([geight_n_dos])], ignore_index=True)
    versus_time_row = hs_df[hs_df["versus_time"] == hs_df["versus_time"].max()]

    awards_list.append(
        {
            "class": "versus-time",
            "name": "Versus Time",
            "player_name": versus_time_row["player_name"].item(),
            "player_id": versus_time_row["player_id"].item(),
            "value": f"{versus_time_row['versus_time'].item()/60/60:.0f} hours of local versus",
        }
    )

    practice_time_row = hs_df[hs_df["practice_time"] == hs_df["practice_time"].max()]
    awards_list.append(
        {
            "class": "practice-time",
            "name": "Head Trainer",
            "player_name": practice_time_row["player_name"].item(),
            "player_id": practice_time_row["player_id"].item(),
            "value": f"{practice_time_row['practice_time'].item()/60/60:.0f} hours of practice",
        }
    )

    arcade_time_row = hs_df[hs_df["arcade_time"] == hs_df["arcade_time"].max()]
    awards_list.append(
        {
            "class": "arcade-time",
            "name": "Cabinet Critter",
            "player_name": arcade_time_row["player_name"].item(),
            "player_id": arcade_time_row["player_id"].item(),
            "value": f"{arcade_time_row['arcade_time'].item()/60/60:.0f} hours of arcade",
        }
    )

    wt_time_row = hs_df[hs_df["wt_time"] == hs_df["wt_time"].max()]
    awards_list.append(
        {
            "class": "wt-time",
            "name": "World (Tour) Warrior",
            "player_name": wt_time_row["player_name"].item(),
            "player_id": wt_time_row["player_id"].item(),
            "value": f"{wt_time_row['wt_time'].item()/60/60:.0f} hours of World Tour",
        }
    )

    thumbs_row = hs_df[hs_df["thumbs"] == hs_df["thumbs"].max()]
    awards_list.append(
        {
            "class": "thumbs",
            "name": '"Nice Guy"',
            "player_name": thumbs_row["player_name"].item(),
            "player_id": thumbs_row["player_id"].item(),
            "value": f"{int(thumbs_row['thumbs'].item()):,} 👍",
        }
    )

    return awards_list
