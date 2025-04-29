import PlayerSchema from "../../schemas/PlayerSchema"
import CharIcon from "./CharIcon";

const PlayerCard = ({ player_id, player_name, last_played, selected_char }: PlayerSchema) => {
    return (
        <div className="col">
            <div className="card" key={player_id}>
                <CharIcon selected_char={selected_char} />
                <div className="card-body">
                    <h5 className="card-title">{player_name}</h5>
                </div>
                <div className="card-footer text-body-secondary">
                    Last Played {last_played}
                </div>
            </div>
        </div>
    )
}

export default PlayerCard