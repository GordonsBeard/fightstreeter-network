import club_logo from '../assets/img/club_logo.png';
import ClubRoster from '../components/ClubRoster';

const ClubRosterPage = () => {
    return (
        <div className="text-center p-3">
            <img src={club_logo} className="rounded mx-auto d-block" />
            <h2 className="h3 mb-3">Funny Animals Roster</h2>
            <ClubRoster />
        </div>
    )
}

export default ClubRosterPage