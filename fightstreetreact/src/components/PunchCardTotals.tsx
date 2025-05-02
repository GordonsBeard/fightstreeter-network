import PunchCardSchema from '../schemas/PunchCardSchema'
import { addCommas, convertToHours } from '../utils'

function PunchCardTotals(punchCard: PunchCardSchema) {

    return (
        <>
            <ul className="list-group list-group-flush">
                {punchCard.thumbs_gained > 0 && <li className="list-group-item"><strong>+{punchCard.thumbs_gained}</strong> <i className="bi bi-hand-thumbs-up"></i></li>}
                {punchCard.kudos_gained > 1 && <li className="list-group-item">Kudos: <strong>+{addCommas(punchCard.kudos_gained)}</strong></li>}
                {punchCard.total_matches > 0 && <li className="list-group-item">Total Matches: <strong>{punchCard.total_matches}</strong> ({convertToHours(punchCard.total_time)})</li>}
                {punchCard.hub_matches > 0 && <li className="list-group-item">Hub Matches: <strong>{punchCard.hub_matches}</strong> ({convertToHours(punchCard.hub_time)})</li>}
                {punchCard.casual_matches > 0 && <li className="list-group-item">Casual Matches: <strong>{punchCard.casual_matches}</strong>  ({convertToHours(punchCard.casual_time)})</li>}
                {punchCard.ranked_matches > 0 && <li className="list-group-item">Ranked Matches: <strong>{punchCard.ranked_matches}</strong>  ({convertToHours(punchCard.ranked_time)})</li>}
                {punchCard.custom_matches > 0 && <li className="list-group-item">Custom Room Matches: <strong>{punchCard.custom_matches}</strong>  ({convertToHours(punchCard.custom_time)})</li>}
                {punchCard.practice_time > 1 && <li className="list-group-item">Practice Time: <strong>{convertToHours(punchCard.practice_time)}</strong></li>}
                {punchCard.versus_time > 1 && <li className="list-group-item">Versus Time: <strong>{convertToHours(punchCard.versus_time)}</strong></li>}
                {punchCard.extreme_time > 1 && <li className="list-group-item">Extreme Time: <strong>{convertToHours(punchCard.extreme_time)}</strong></li>}
                {punchCard.arcade_time > 0 && <li className="list-group-item">Arcade Time: <strong>{convertToHours(punchCard.arcade_time)}</strong></li>}
                {punchCard.wt_time > 0 && <li className="list-group-item">World Tour Time: <strong>{convertToHours(punchCard.wt_time)}</strong></li>}
            </ul>
        </>
    )
}

export default PunchCardTotals