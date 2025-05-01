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
        <>
            <div style={{ gridTemplateColumns: "1fr 1fr 1fr" }} className="d-grid gap-2 text-center mb-3 pt-3">
                <div className="card d-flex align-middle">
                    <div className="card-body">
                        <h6 className="card-title">Casual</h6>
                        <h6 className="card-subtitle text-body-secondary">
                            {addCommas(overview.casual_matches)}
                        </h6>
                    </div>
                </div>
                <div className="card">
                    <div className="card-body">
                        <h6 className="card-title">Hub</h6>
                        <h6 className="card-subtitle text-body-secondary">
                            {addCommas(overview.hub_matches)}
                        </h6>
                    </div>
                </div>
                <div className="card">
                    <div className="card-body">
                        <h6 className="card-title">Ranked</h6>
                        <h6 className="card-subtitle text-body-secondary">
                            {addCommas(overview.ranked_matches)}
                        </h6>
                    </div>
                </div>
            </div>
            <table className="table table-sm">
                <tbody>
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
            <h4 className="text-center m-3">Time Played</h4>
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
        </>
    )
}

export default PlayerSummaryTable