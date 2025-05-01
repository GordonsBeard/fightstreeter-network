import HistoricStatsSchema from "../schemas/HistoricStatsSchema";
import { useEffect, useState } from "react";
import axios from "axios";
import PlayerSummaryTable from "../components/ui/PlayerSummaryTable";
import PlayerSummaryHeader from "../components/ui/PlayerSummaryHeader";
import DateSelector from "../components/ui/DateSelector";

const PlayerDashPage = () => {
    const [overview, setOverview] = useState<HistoricStatsSchema>({
        date: "2024-04-00",
        arcade_time: 600,
        custom_matches: 100,
        casual_matches: 10,
        casual_time: 600,
        custom_time: 600,
        date_joined: "2023-06-02",
        extreme_time: 600,
        hub_matches: 10,
        hub_time: 600,
        last_played: "2024-04-18",
        player_id: "1001001000",
        player_name: "Player (1)",
        practice_time: 600,
        profile_tagline: "no way jose",
        ranked_matches: 10,
        ranked_time: 600,
        selected_character: "Gordon",
        selected_lp: 25000,
        selected_mr: 1500,
        thumbs: 68,
        title_plate: "something-stringy",
        title_text: "The Big Bossy Is Hossy",
        total_kudos: 420,
        versus_time: 600,
        wt_time: 6000
    })

    const fetchPlayerOverview = async () => {
        const response = await axios.get<[HistoricStatsSchema]>("http://localhost:5000/player/overview?player_id=3425126856&date_start=2025-04-20&date_end=2025-04-20&fetch_range=false")
        const playerOverview = response.data;
        const todaysOverview = playerOverview[0];
        setOverview(todaysOverview);
    }

    useEffect(() => {
        fetchPlayerOverview()
    }, []);

    return (
        <>
            <div className="row">
                <PlayerSummaryHeader {...overview} />
            </div>
            <div className="row mx-0">
                <ul className="nav nav-tabs" id="playerTab" role="tablist">
                    <li className="nav-item" role="presentation">
                        <button className="nav-link active" id="totals-tab" data-bs-toggle="tab" data-bs-target="#totals-tab-pane" type="button" role="tab" aria-controls="totals-tab-pane" aria-selected="true">Totals</button>
                    </li>
                    <li className="nav-item" role="presentation">
                        <button className="nav-link" id="card-tab" data-bs-toggle="tab" data-bs-target="#card-tab-pane" type="button" role="tab" aria-controls="card-tab-pane" aria-selected="false">Punch Card</button>
                    </li>
                    <li className="nav-item" role="presentation">
                        <button className="nav-link" id="graphs-tab" data-bs-toggle="tab" data-bs-target="#graphs-tab-pane" type="button" role="tab" aria-controls="contact-tab-pane" aria-selected="false">Graphs</button>
                    </li>
                </ul>
                <div className="tab-content" id="playerTabContent">
                    <div className="tab-pane show active" id="totals-tab-pane" role="tabpanel" aria-labelledby="totals-tab" tabIndex={0}>
                        <PlayerSummaryTable {...overview} />
                    </div>
                    <div className="tab-pane" id="card-tab-pane" role="tabpanel" aria-labelledby="card-tab" tabIndex={0}>
                        <DateSelector />
                    </div>
                    <div className="tab-pane" id="graphs-tab-pane" role="tabpanel" aria-labelledby="graphs-tab" tabIndex={0}>
                        <DateSelector />
                    </div>
                </div>
            </div>
        </>
    )
}

export default PlayerDashPage