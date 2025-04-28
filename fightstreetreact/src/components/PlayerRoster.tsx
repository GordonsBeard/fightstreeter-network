import { useEffect, useState } from 'react'
import PlayerSchema from '../schemas/PlayerSchema';
import axios from 'axios';


function PlayerList() {
    const [users, setUsers] = useState<[PlayerSchema]>([{
        last_played: "000", player_id: "000", player_name: "None"
    }]);

    const fetchClubRoster = async () => {
        const response = await axios.get<[PlayerSchema]>("http://localhost:5000/roster/");
        const users = response.data;
        setUsers(users);
    };


    useEffect(() => {
        fetchClubRoster()
    }, [])

    return (
        <>
            {
                users.map((user: PlayerSchema) => (
                    <a key={user.player_id}>{user.player_name}</a>
                ))
            }
        </>
    )
}

export default PlayerList
