import PunchCardSchema from '../schemas/PunchCardSchema'
import { convertToHours, punchCardNumber } from '../utils';
import PunchCardTotals from './PunchCardTotals';

function PunchCard(punchCard: PunchCardSchema) {
    if (punchCard.total_time == 0 && punchCard.thumbs_gained == 0) {
        return (
            <>
                <p className="text-secondary-emphasis">No punch card data logged for this time period!</p>
            </>
        )
    }

    return (
        <>
            < div className="card">
                <dl className="row m-0 pt-2 border-bottom border-secondary-subtle">
                    <dt className="col-3 text-secondary">NAME</dt>
                    <dd className="col-9">{punchCard.player_name}</dd>
                    <dt className="col-3 text-secondary">LOGGED</dt>
                    <dd className="col-9">{convertToHours(punchCard.total_time)}</dd>
                </dl>

                <p className="small text-center text-secondary mb-1"><em>Activity measured from {punchCard.prev_date} to {punchCard.date}</em></p>
                <PunchCardTotals {...punchCard} />
                <div className="card-body border-bottom">
                    <h3 className="card-title text-center"><i className="bi bi-joystick"></i> HUB CRITTER</h3>
                </div>
                <div className="card-body">
                    <h5 className="card-title text-end">PUNCH CARD</h5>
                    <h6 className="card-subtitle text-body-secondary text-end">{punchCardNumber(punchCard.prev_date, punchCard.player_id)}</h6>
                </div>
            </div >
        </>
    )
}

export default PunchCard