import HistoricStatsSchema from '../../schemas/HistoricStatsSchema'

function convertToHours(stat: number | undefined): string {
    const realValue = stat ? stat : 0;
    return (realValue / 3600).toFixed(2).toLocaleString() + " Hours";
}

function addCommas(stat: number | undefined): string {
    const realValue = stat ? stat : 0;
    return realValue.toLocaleString();
}

function PlayerSummaryTable(overview: HistoricStatsSchema) {
    return (
        <div className="p-2">
            <h3>Totals</h3>
            <table className="table table-sm">
                <tbody>
                    <tr>
                        <th scope="row">Casual Matches</th>
                        <td>{addCommas(overview.casual_matches)}</td>
                    </tr>

                    <tr>
                        <th scope="row">Hub Matches</th>
                        <td>{addCommas(overview.hub_matches)}</td>
                    </tr>
                    <tr>
                        <th scope="row">Ranked Matches</th>
                        <td>{addCommas(overview.ranked_matches)}</td>
                    </tr>
                    <tr>
                        <th scope="row">Likes</th>
                        <td>{addCommas(overview.thumbs)} 👍</td>
                    </tr>
                    <tr>
                        <th scope="row">Total Kudos</th>
                        <td>{addCommas(overview.total_kudos)}</td>
                    </tr>
                </tbody>
            </table>

            <h3>Time Played</h3>
            <table className="table table-sm">
                <tbody>
                    <tr>
                        <th scope="row">Arcade Time</th>
                        <td>{convertToHours(overview.arcade_time)}</td>
                    </tr>
                    <tr>
                        <th scope="row">Casual Time</th>
                        <td>{convertToHours(overview.casual_time)}</td>
                    </tr>
                    <tr>
                        <th scope="row">Custom Time</th>
                        <td>{convertToHours(overview.custom_time)}</td>
                    </tr>
                    <tr>
                        <th scope="row">Extreme Time</th>
                        <td>{convertToHours(overview.extreme_time)}</td>
                    </tr>
                    <tr>
                        <th scope="row">Practice Time</th>
                        <td>{convertToHours(overview.practice_time)}</td>
                    </tr>
                    <tr>
                        <th scope="row">Ranked Time</th>
                        <td>{convertToHours(overview.ranked_time)}</td>
                    </tr>
                    <tr>
                        <th scope="row">Versus Time</th>
                        <td>{convertToHours(overview.versus_time)}</td>
                    </tr>
                    <tr>
                        <th scope="row">World Tour Time</th>
                        <td>{convertToHours(overview.wt_time)}</td>
                    </tr>

                </tbody>
            </table>
        </div>
    )
}

export default PlayerSummaryTable