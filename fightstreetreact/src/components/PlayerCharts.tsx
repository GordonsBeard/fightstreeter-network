import { useEffect, useState } from 'react'
import Plot from 'react-plotly.js';
import axios from 'axios';

interface Props {
    player_id: string;
    player_name: string;
    phase: number;
}

function PlayerCharts({ player_id, player_name, phase }: Props) {
    const [playerGraph, setPlayerGraph] = useState(null);

    useEffect(() => {
        async function fetchPlayerGraph() {
            const response = await axios.get(`http://localhost:5000/player/ranking/graph?player_id=${player_id}&date_start=X&date_end=X&phase=${phase}&fetch_range=true`, { validateStatus: function (status) { return status < 500; } });
            const rankings = response.data;
            setPlayerGraph(rankings);
        }
        fetchPlayerGraph();
    }, [player_id, phase])

    if (!playerGraph || !playerGraph["lp"]) {
        return (
            <>
                <div className="row">
                    <p>No data for this phase!</p>
                </div>
            </>
        )
    }

    return (
        <>
            <div className="row pb-6" >
                <h3>League Points</h3>
                <Plot
                    data={playerGraph["lp"].data}
                    layout={playerGraph["lp"].layout}
                    config={{ responsive: true }}
                    useResizeHandler={true}
                    className="col"
                />
            </div>
            <div className="row">
                <h3>Master Rate</h3>
                {playerGraph["mr"] &&
                    <Plot
                        data={playerGraph["mr"].data}
                        layout={playerGraph["mr"].layout}
                        config={{ responsive: true }}
                        useResizeHandler={true}
                        className="col"
                    />}
            </div>
        </>
    )
}

export default PlayerCharts