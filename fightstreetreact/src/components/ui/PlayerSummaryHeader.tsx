import HistoricStatsSchema from '../../schemas/HistoricStatsSchema'
import characterCardImage from '../../utils'
import CharIcon from './CharIcon'

function PlayerSummaryHeader(overview: HistoricStatsSchema) {
    return (
        <>
            <div style={{ backgroundColor: "#000000", backgroundImage: `url(${characterCardImage.get(overview.selected_character)})`, backgroundRepeat: "no-repeat", backgroundPosition: "80% 0%" }}>
                <div className="row mx-2">
                    <h1 className="text-end p-3 pb-0 mb-0">{overview?.player_name}</h1>
                    <a className="text-end link-opacity-50 fs-6" href={"https://www.streetfighter.com/6/buckler/profile/" + overview.player_id}>CFN ID#: {overview.player_id}</a>
                </div>
            </div>

            <p>{overview.profile_tagline}</p>
            <p>Current character: {overview.selected_character}</p>
            <p>{overview.title_text}</p>
        </>
    )
}

export default PlayerSummaryHeader