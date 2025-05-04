import { useEffect, useState } from 'react'
import Plot from 'react-plotly.js';
import PlayerRankingSchema from '../schemas/PlayerRankingSchema';
import axios from 'axios';
import RankingGraphSchema from '../schemas/RankingGraphSchema';

interface Props {
    player_id: string;
    player_name: string;
    phase: number;
}

function PlayerCharts({ player_id, player_name, phase }: Props) {
    const [playerRankings, setPlayerRankings] = useState<RankingGraphSchema | null>(null);

    useEffect(() => {
        async function fetchPlayerRankings() {
            const response = await axios.get<RankingGraphSchema>(`http://localhost:5000/player/ranking/graph?player_id=${player_id}&date_start=X&date_end=X&phase=${phase}&fetch_range=true`);
            const rankings = response.data;
            setPlayerRankings(rankings);
        }
        fetchPlayerRankings();
    }, [player_id, phase])
    if (!playerRankings) {
        return null;
    }
    return (
        <>
            <div className="row">
                <Plot
                    data={[
                        {
                            x: playerRankings.all_dates,
                            y: [300, 400, 300, 200],
                            type: 'scatter',
                            mode: 'lines',
                            marker: { color: 'red' },
                        },
                    ]}
                    layout={{
                        width: 320,
                        title: { text: `${player_name} (Phase ${phase})` },
                        autosize: true,
                        margin: { l: 60, b: 20, r: 20, t: 80 },
                        showlegend: true,
                        legend: { "orientation": "h" },
                        xaxis: {
                            ticks: 'outside',
                            tick0: 0,
                            ticklen: 8,
                            dtick: 0.25,
                        }
                    }}
                    config={{ responsive: true }}
                    useResizeHandler={true}
                    className="col"
                />
            </div>
        </>
    )
}

export default PlayerCharts