import HistoricStatsSchema from "../schemas/HistoricStatsSchema";
import { useEffect, useState } from "react";
import axios from "axios";
import PlayerSummaryTable from "../components/ui/PlayerSummaryTable";
import PlayerSummaryHeader from "../components/ui/PlayerSummaryHeader";
import DateSelector from "../components/ui/DateSelector";

const PlayerDashPage = () => {
    const [overview, setOverview] = useState<HistoricStatsSchema>()

    const fetchPlayerOverview = async () => {
        const response = await axios.get<[HistoricStatsSchema]>("http://localhost:5000/player/overview?player_id=3425126856&date_start=2025-04-20&date_end=2025-04-20&fetch_range=false")
        const playerOverview = response.data;
        const todaysOverview = playerOverview[0];
        setOverview(todaysOverview);
        console.log(todaysOverview)
    }

    useEffect(() => {
        fetchPlayerOverview()
    }, []);

    return (

        <div className="p-2">
            <h2 className="text-center p-3 mb-0">{overview?.player_name}</h2>

            <PlayerSummaryHeader {...overview} />

            <DateSelector date={overview?.date!} />

            <div className="row p3 m3">
                <PlayerSummaryTable {...overview} />
            </div>
        </div>
    )
}

export default PlayerDashPage