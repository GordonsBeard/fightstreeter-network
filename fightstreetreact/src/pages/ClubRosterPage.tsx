import club_logo from '../assets/img/club_logo.png';
import PlayerRoster from '../components/PlayerRoster';

const ClubRosterPage = () => {
    return (
        <div className="text-center">
            <img src={club_logo} className="rounded mx-auto d-block" />
            <h2 className="h3">Funny Animals Roster</h2>
            <PlayerRoster users={[]} />
        </div>
    )
}

export default ClubRosterPage