export interface HistoricStatsSchema {
    arcade_time: number;
    casual_matches: number;
    casual_time: number;
    custom_matches: number;
    custom_time: number;
    date: string;
    date_joined: string;
    extreme_time: number;
    hub_matches: number;
    hub_time: number;
    last_played: string;
    player_id: string;
    player_name: string;
    practice_time: number;
    profile_tagline: string;
    ranked_matches: number;
    ranked_time: number;
    selected_character: string;
    selected_lp: number;
    selected_mr: number;
    thumbs: number;
    title_plate: string;
    title_text: string;
    total_kudos: number;
    versus_time: number;
    wt_time: number;
}

export default HistoricStatsSchema;