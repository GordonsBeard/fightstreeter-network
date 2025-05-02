import PunchCardSchema from '../schemas/PunchCardSchema'
import PunchCardFooter from './PunchCardFooter';
import PunchCardTotals from './PunchCardTotals';
import PunchCardStamp from './PunchCardStamp';
import { convertToHours } from '../utils';

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
                <PunchCardStamp {...punchCard} />
                <PunchCardFooter {...punchCard} />
            </div >
        </>
    )
}

export default PunchCard