"""Generate the awards for today."""

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

    hs_df: pd.DataFrame = pd.read_sql_query(historic_stats_sql, conn)
    conn.close()

    hs_df["selected_char"] = hs_df["selected_char"].replace(charid_map)

    if len(hs_df.values) == 0:
        return awards_list

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
            "name": "No Strings Attached",
            "player_name": casual_matches_row["player_name"].item(),
            "player_id": casual_matches_row["player_id"].item(),
            "value": f"{casual_matches_row['ranked_matches'].item():,} casual matches",
        }
    )

    extreme_time_row = hs_df[hs_df["extreme_time"] == hs_df["extreme_time"].max()]
    awards_list.append(
        {
            "class": "extreme-time",
            "name": "X-Games Mode",
            "player_name": extreme_time_row["player_name"].item(),
            "player_id": extreme_time_row["player_id"].item(),
            "value": f"{extreme_time_row['extreme_time'].item()/60:.0f} minutes of Extreme Battles",
        }
    )

    versus_time_row = hs_df[hs_df["versus_time"] == hs_df["versus_time"].max()]
    awards_list.append(
        {
            "class": "versus-time",
            "name": "Touched Grass",
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
            "class": "thumbs-time",
            "name": '"Nice Guy"',
            "player_name": thumbs_row["player_name"].item(),
            "player_id": thumbs_row["player_id"].item(),
            "value": f"{thumbs_row['thumbs'].item():,} 👍",
        }
    )

    return awards_list
