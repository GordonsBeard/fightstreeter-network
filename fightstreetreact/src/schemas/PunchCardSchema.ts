interface RankedResult {
    lp: number;
    mr: number;
}

export interface PunchCardSchema {
    player_name: string;
    player_id: string;
    date: string;
    prev_date: string;
    arcade_time: number;
    casual_matches: number;
    casual_time: number;
    custom_matches: number;
    custom_time: number;
    extreme_time: number;
    hub_matches: number;
    hub_time: number;
    kudos_gained: number;
    practice_time: number;
    ranked_matches: number;
    ranked_time: number;
    selected_char: string;
    thumbs_gained: number;
    total_matches: number;
    total_time: number;
    versus_time: number;
    wt_time: number;
    ranked_changes: { [key: string]: RankedResult }
}

export default PunchCardSchema