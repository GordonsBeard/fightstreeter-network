import { useEffect, useState } from 'react'
import PlayerSchema from '../schemas/PlayerSchema';
import axios from 'axios';
import PlayerCard from './PlayerCard';


function PlayerList() {
    const [users, setUsers] = useState<[PlayerSchema]>([{
        last_played: "000", player_id: "000", player_name: "None", selected_char: "Random"
    }]);

    const fetchClubRoster = async () => {
        const response = await axios.get<[PlayerSchema]>("http://localhost:5000/roster/");
        const users = response.data;
        setUsers(users);
    };

    useEffect(() => {
        fetchClubRoster()
    }, []);

    return (
        <>
            <div className="row row-cols-2 row-cols-md-4 g-3">
                {
                    users.map((user: PlayerSchema) => (
                        <PlayerCard
                            key={user.player_id}
                            player_id={user.player_id}
                            player_name={user.player_name}
                            last_played={user.last_played}
                            selected_char={user.selected_char} />
                    ))
                }
            </div>
        </>
    )
}

export default PlayerList
