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

    # battle hub
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

    return awards_list
