import HistoricStatsSchema from '../../schemas/HistoricStatsSchema'
import CharIcon from './CharIcon'

function PlayerSummaryHeader(overview: HistoricStatsSchema) {
    return (
        <div className="text-center">
            <a href={"https://www.streetfighter.com/6/buckler/profile/" + overview.player_id} className="link-opacity-50">CFN ID#: {overview.player_id}</a>
            <p>{overview.profile_tagline}</p>
            <CharIcon selected_char={overview.selected_character}
                style={{ objectFit: "cover", height: 125, width: 300 }} />
            <p>Current character: {overview.selected_character}</p>
            <p>{overview.title_text}</p>
        </div>
    )
}

export default PlayerSummaryHeader