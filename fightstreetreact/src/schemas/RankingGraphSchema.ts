interface RankingGraphSchema {
    all_dates: string[];
    characters: { [char_name: string]: { [dates: string]: string[] } };
}

export default RankingGraphSchema