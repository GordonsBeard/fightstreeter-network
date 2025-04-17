DROP TABLE IF EXISTS club_members;
DROP TABLE IF EXISTS ranking;
DROP TABLE IF EXISTS historic_stats;
DROP TABLE IF EXISTS last_update;

CREATE TABLE IF NOT EXISTS club_members (
    club_id TEXT NOT NULL,
    player_name TEXT NOT NULL,
    player_id TEXT NOT NULL,
    joined_at TEXT,
    position INTEGER NOT NULL,
    hidden INTEGER DEFAULT 0 NOT NULL,
    unique(club_id, player_id)
);

CREATE TABLE IF NOT EXISTS ranking (
    date TEXT NOT NULL,
    phase INTEGER NOT NULL,
    player_id TEXT NOT NULL,
    char_id TEXT NOT NULL,
    lp INTEGER,
    mr INTEGER,
    unique(player_id, char_id, date)
);

CREATE TABLE IF NOT EXISTS historic_stats (
    date TEXT NOT NULL,
    player_id TEXT NOT NULL,
    player_name TEXT NOT NULL,

    selected_char TEXT NOT NULL,
    lp INTEGER,
    mr INTEGER,

    hub_matches INTEGER,
    ranked_matches INTEGER,
    casual_matches INTEGER,
    custom_matches INTEGER,

    hub_time INTEGER,
    ranked_time INTEGER,
    casual_time INTEGER,
    custom_time INTEGER,
    extreme_time INTEGER,
    versus_time INTEGER,
    practice_time INTEGER,
    arcade_time INTEGER,
    wt_time INTEGER,

    total_kudos INTEGER,
    thumbs INTEGER,
    last_played TEXT NOT NULL,
    profile_tagline TEXT,
    title_text TEXT,
    title_plate TEXT,

    unique(date, player_id)
);

CREATE TABLE IF NOT EXISTS last_update (
    date TEXT PRIMARY KEY,
    download_complete INTEGER DEFAULT 0 NOT NULL,
    parsing_complete INTEGER DEFAULT 0 NOT NULL
);
