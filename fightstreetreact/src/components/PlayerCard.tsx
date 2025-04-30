import PlayerSchema from "../schemas/PlayerSchema"
import CharIcon from "./ui/CharIcon";

const PlayerCard = ({ player_id, player_name, last_played, selected_char }: PlayerSchema) => {
    return (
        <div className="col">
            <div className="card" key={player_id}>
                <CharIcon selected_char={selected_char} />
                <div className="card-footer text-body-secondary">
                    <a href={"/player/" + player_id} className="stretched-link">{player_name}</a>
                </div>
            </div>
        </div>
    )
}

export default PlayerCard