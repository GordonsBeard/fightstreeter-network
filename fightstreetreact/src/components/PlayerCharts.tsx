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
            const response = await axios.get(`http://localhost:5000/player/ranking/graph?player_id=${player_id}&date_start=X&date_end=X&phase=${phase}&fetch_range=true`);
            const rankings = response.data;
            setPlayerGraph(rankings);
        }
        fetchPlayerGraph();
    }, [player_id, phase])

    if (!playerGraph) {
        return null;
    }

    return (
        <>
            <div className="row">
                <Plot
                    data={playerGraph["lp"].data}
                    layout={playerGraph["lp"].layout}
                    config={{ responsive: true }}
                    useResizeHandler={true}
                    className="col"
                />
            </div>
            <div className="row">
                <Plot
                    data={playerGraph["mr"].data}
                    layout={playerGraph["mr"].layout}
                    config={{ responsive: true }}
                    useResizeHandler={true}
                    className="col"
                />
            </div>
        </>
    )
}

export default PlayerCharts