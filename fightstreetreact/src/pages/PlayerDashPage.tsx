import Plot from "react-plotly.js";
import HistoricStatsSchema from "../schemas/HistoricStatsSchema";
import { useEffect, useState } from "react";
import axios from "axios";

const PlayerDashPage = () => {
    const [overview, setOverview] = useState<HistoricStatsSchema>()

    const fetchPlayerOverview = async () => {
        const response = await axios.get<[HistoricStatsSchema]>("http://localhost:5000/player/overview?player_id=3425126856&date_start=2025-04-01&date_end=2025-04-17&fetch_range=false")
        const playerOverview = response.data;
        const todaysOverview = playerOverview[0];
        setOverview(todaysOverview);
        console.log(todaysOverview)
    }

    useEffect(() => {
        fetchPlayerOverview()
    }, []);

    return (
        <>
            <h3>{overview?.player_name}</h3>
            <p>ID#: {overview?.player_id}</p>
            <p>{overview?.profile_tagline}</p>
            <p>Currently character: {overview?.selected_character}</p>
            <p>{overview?.title_text}</p>
            <table className="table">
                <thead>
                    <tr>
                        <th scope="col">Category</th>
                        <th scope="col">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <th scope="row">Arcade Time</th>
                        <td>{(overview?.arcade_time! / 3600).toFixed(2).toLocaleString()} Hours</td>
                    </tr>
                    <tr>
                        <th scope="row">Casual Matches</th>
                        <td>{overview?.casual_matches.toLocaleString()}</td>
                    </tr>
                    <tr>
                        <th scope="row">Casual Time</th>
                        <td>{(overview?.casual_time! / 3600).toFixed(2).toLocaleString()} Hours</td>
                    </tr>

                    <tr>
                        <th scope="row">Custom Time</th>
                        <td>{(overview?.custom_time! / 3600).toFixed(2).toLocaleString()} Hours</td>
                    </tr>

                    <tr>
                        <th scope="row">Extreme Time</th>
                        <td>{(overview?.extreme_time! / 3600).toFixed(2).toLocaleString()} Hours</td>
                    </tr>

                    <tr>
                        <th scope="row">Hub Matches</th>
                        <td>{overview?.hub_matches.toLocaleString()}</td>
                    </tr>
                    <tr>
                        <th scope="row">Practice Time</th>
                        <td>{(overview?.practice_time! / 3600).toFixed(2).toLocaleString()}</td>
                    </tr>
                    <tr>
                        <th scope="row">Ranked Matches</th>
                        <td>{overview?.ranked_matches.toLocaleString()}</td>
                    </tr>
                    <tr>
                        <th scope="row">Ranked Time</th>
                        <td>{(overview?.ranked_time! / 3600).toFixed(2).toLocaleString()}</td>
                    </tr>
                    <tr>
                        <th scope="row">Likes</th>
                        <td>{overview?.thumbs.toLocaleString()} 👍</td>
                    </tr>
                    <tr>
                        <th scope="row">Total Kudos</th>
                        <td>{overview?.total_kudos.toLocaleString()}</td>
                    </tr>
                    <tr>
                        <th scope="row">Versus Time</th>
                        <td>{(overview?.versus_time! / 3600).toFixed(2).toLocaleString()}</td>
                    </tr>
                    <tr>
                        <th scope="row">World Tour Time</th>
                        <td>{(overview?.wt_time! / 3600).toFixed(2).toLocaleString()}</td>
                    </tr>
                </tbody>
            </table>
            <Plot
                data={[
                    {
                        x: [1, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18],
                        y: [32, 37, 40.5, 43, 49, 54, 59, 63.5, 69.5, 73, 74],
                        mode: "markers",
                        type: "scatter",
                    },
                ]}
                layout={{
                    title: "Growth Rate in Boys",
                    xaxis: {
                        title: "Age (years)",
                    },
                    yaxis: {
                        title: "Height (inches)",
                    },
                }}
            />
        </>
    )
}

export default PlayerDashPage