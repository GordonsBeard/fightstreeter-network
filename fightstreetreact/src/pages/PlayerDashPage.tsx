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
            <p>Currently character: </p>
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
                        <td>50 hours</td>
                    </tr>
                    <tr>
                        <th scope="row">Arcade Time</th>
                        <td>50 hours</td>
                    </tr>
                    <tr>
                        <th scope="row">Arcade Time</th>
                        <td>50 hours</td>
                    </tr>
                    <tr>
                        <th scope="row">Arcade Time</th>
                        <td>50 hours</td>
                    </tr>
                    <tr>
                        <th scope="row">Arcade Time</th>
                        <td>50 hours</td>
                    </tr>
                    <tr>
                        <th scope="row">Arcade Time</th>
                        <td>50 hours</td>
                    </tr>
                    <tr>
                        <th scope="row">Arcade Time</th>
                        <td>50 hours</td>
                    </tr>
                    <tr>
                        <th scope="row">Arcade Time</th>
                        <td>50 hours</td>
                    </tr>
                    <tr>
                        <th scope="row">Arcade Time</th>
                        <td>50 hours</td>
                    </tr>
                    <tr>
                        <th scope="row">Arcade Time</th>
                        <td>50 hours</td>
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