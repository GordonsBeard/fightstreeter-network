import HistoricStatsSchema from "../schemas/HistoricStatsSchema";
import { useParams } from "react-router-dom";
import { useContext, useEffect, useState } from "react";
import axios from "axios";
import PlayerSummaryTable from "../components/ui/PlayerSummaryTable";
import PlayerSummaryHeader from "../components/ui/PlayerSummaryHeader";
import PunchCard from "../components/PunchCard";
import { DatesContext } from '../schemas/ValidDatesContext';
import DateSelector from "../components/ui/DateSelector";
import PunchCardSchema from "../schemas/PunchCardSchema";

const PlayerDashPage = () => {
    const { playerId } = useParams();
    const validDates = useContext(DatesContext);
    const latestDate = validDates.dates[0];
    const [overview, setOverview] = useState<HistoricStatsSchema | null>(null)
    const [punchCard, setPunchCard] = useState<PunchCardSchema | null>(null);
    const [punchCardDate, setPunchCardDate] = useState('');

    useEffect(() => {
        async function fetchPlayerOverview() {
            const response = await axios.get<[HistoricStatsSchema]>(`http://localhost:5000/player/overview?player_id=${playerId}&date_start=${latestDate}&date_end=${latestDate}&fetch_range=false`)
            const playerOverview = response.data;
            const todaysOverview = playerOverview[0];
            setOverview(todaysOverview);
        }
        fetchPlayerOverview()
        setPunchCardDate(validDates.dates[0])

    }, [playerId, latestDate, validDates]);

    useEffect(() => {
        const fetchPunchCard = async () => {
            if (!punchCardDate) {
                setPunchCard(null);
                return;
            }

            const response = await axios.get<PunchCardSchema>(`http://localhost:5000/punchcard?player_id=${playerId}&date=${punchCardDate}`);
            setPunchCard(response.data);

        }
        fetchPunchCard()
    }, [playerId, punchCardDate])

    const handleDateChange = (value: string) => {
        setPunchCardDate(value);
    }

    if (!overview) {
        return null;
    }

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
                        <DateSelector dateValue={punchCardDate} handleDateChange={handleDateChange} />
                        {punchCard &&
                            <PunchCard {...punchCard} />}
                    </div>
                    <div className="tab-pane" id="graphs-tab-pane" role="tabpanel" aria-labelledby="graphs-tab" tabIndex={0}>
                    </div>
                </div>
            </div>
            <div className="row p-3">
                <p className="text-secondary small">Your PunchCard represents everything you've done on CFN for the period logged. These include Ranked, Hub, Casual, and custom matches. Offline activities such as versus time and extreme time are also tracked.</p>
                <p className="text-secondary small">FSN PunchCards are generated around 12pm PST.</p>
            </div>
        </>
    )
}

export default PlayerDashPage