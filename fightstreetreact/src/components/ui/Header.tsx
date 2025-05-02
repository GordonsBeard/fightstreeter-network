import { FC } from "react";

const Header: FC = () => {
    return (
        <>
            <nav className="navbar navbar-expand-sm bg-body-tertiary">
                <div className="container-fluid">
                    <span className="navbar-brand">FIGHT STREETER NETWORK</span>
                    <button className="navbar-toggler"
                        type="button"
                        data-bs-toggle="collapse"
                        data-bs-target="#navbarNavAltMarkup"
                        aria-controls="navbarNavAltMarkup"
                        aria-expanded="false"
                        aria-label="Toggle navigation">
                        <span className="navbar-toggler-icon"></span>
                    </button>
                    <div className="collapse navbar-collapse" id="navbarNavAltMarkup">
                        <div className="navbar-nav">
                            <a className="nav-link" href="/roster">Club Roster</a>
                            <a className="nav-link" href="/leaderboards">Leaderboards</a>
                        </div>
                    </div>
                </div>
            </nav>
        </>
    )
}

export default Header;