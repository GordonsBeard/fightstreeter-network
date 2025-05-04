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
import PlayerCharts from "../components/PlayerCharts";
import { PhasesContext } from "../schemas/ValidPhasesContext";

const PlayerDashPage = () => {
    const { playerId } = useParams();
    const validDates = useContext(DatesContext);
    const validPhases = useContext(PhasesContext);
    const latestDate = validDates.dates[0];
    const [overview, setOverview] = useState<HistoricStatsSchema | null>(null);
    const [punchCard, setPunchCard] = useState<PunchCardSchema | null>(null);
    const [punchCardDate, setPunchCardDate] = useState('');
    const [graphPhase, setGraphPhase] = useState<number | null>(null);

    useEffect(() => {
        async function fetchPlayerOverview() {
            const response = await axios.get<[HistoricStatsSchema]>(`http://localhost:5000/player/overview?player_id=${playerId}&date_start=${latestDate}&date_end=${latestDate}&phase=0&fetch_range=false`)
            const playerOverview = response.data;
            const todaysOverview = playerOverview[0];
            setOverview(todaysOverview);
        }
        fetchPlayerOverview();
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

    useEffect(() => {
        async function fetchPhaseGraph() {
            if (!graphPhase) {
                setGraphPhase(validPhases.phases[0]);
                return;
            }
        }
        fetchPhaseGraph()
    }, [graphPhase, validPhases.phases])

    const handleDateChange = (value: string) => {
        setPunchCardDate(value);
    }

    const handlePhaseChange = (phase: string) => {
        setGraphPhase(parseInt(phase));
    }

    if (!overview || !playerId || !graphPhase) {
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
                        <select className="form-select m-2" aria-label="Phase selector" onChange={(evt) => { handlePhaseChange(evt.currentTarget.value) }} value={graphPhase}>
                            {validPhases.phases.map((phase: number) => (
                                <option value={phase} key={phase}>Phase {phase}</option>
                            ))};
                        </select>
                        <PlayerCharts player_id={playerId} player_name={overview.player_name} phase={graphPhase} />
                    </div>
                </div>
            </div>
        </>
    )
}

export default PlayerDashPage