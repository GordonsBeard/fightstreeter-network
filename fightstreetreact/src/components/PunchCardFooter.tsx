import PunchCardSchema from '../schemas/PunchCardSchema'
import { punchCardNumber } from '../utils'

function PunchCardFooter(punchCard: PunchCardSchema) {
    return (
        <>
            <div className="card-body">
                <h5 className="card-title text-end">PUNCH CARD</h5>
                <h6 className="card-subtitle text-body-secondary text-end">
                    {punchCardNumber(punchCard.prev_date, punchCard.player_id)}
                </h6>
            </div>
        </>
    )
}

export default PunchCardFooter