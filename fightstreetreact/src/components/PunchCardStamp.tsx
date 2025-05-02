import PunchCardSchema from '../schemas/PunchCardSchema'

function PunchCardStamp(punchCard: PunchCardSchema) {
    const timeList: { name: string, value: number }[] = [
        { name: "arcade", value: punchCard.arcade_time },
        { name: "casual", value: punchCard.casual_time },
        { name: "custom", value: punchCard.custom_time },
        { name: "extreme", value: punchCard.extreme_time },
        { name: "hub", value: punchCard.hub_time },
        { name: "practice", value: punchCard.practice_time },
        { name: "ranked", value: punchCard.ranked_time },
        { name: "versus", value: punchCard.versus_time },
        { name: "wt", value: punchCard.wt_time }
    ]

    const maxTime = timeList.reduce(function (prev, current) {
        return (prev && prev.value > current.value) ? prev : current
    })

    const punchCardStampBook: { [name: string]: string[] } = {
        "arcade": ["bi bi-joystick", "HIGH SCORER"],
        "casual": ["bi bi-joystick", "KEEPING IT CASUAL"],
        "custom": ["bi bi-door-closed", "BACKROOM BRAWLER"],
        "extreme": ["bi bi-exclamation-octagon", "X GAMES MODE"],
        "hub": ["bi bi-chat-right-text", "HUB CRITTER"],
        "practice": ["bi bi-mortarboard", "BACK TO THE LAB AGAIN"],
        "ranked": ["bi bi-trophy", "RISE AND GRIND"],
        "versus": ["bi bi-people-fill", "KEEPING IT LOCAL"],
        "wt": ["bi bi-globe2", "WORLD TOURIST"],
    }

    const matchList: { name: string, value: number }[] = [
        { name: "casual", value: punchCard.casual_matches },
        { name: "custom", value: punchCard.custom_matches },
        { name: "hub", value: punchCard.hub_matches },
        { name: "ranked", value: punchCard.ranked_matches },
    ]

    const maxMatches = matchList.reduce(function (prev, current) {
        return (prev && prev.value > current.value) ? prev : current
    })

    let pcStampLine = (<></>);

    if (maxTime.value > 0) {
        pcStampLine = (<h3 className="card-title text-center"><i className={punchCardStampBook[maxTime.name][0]}></i> {punchCardStampBook[maxTime.name][1]}</h3>)
    } else {
        pcStampLine = (<h3 className="card-title text-center"><i className={punchCardStampBook[maxMatches.name][0]}></i> {punchCardStampBook[maxMatches.name][1]}</h3>)
    }

    return (
        <>
            <div className="card-body border-bottom">
                {pcStampLine}
            </div>
        </>
    )
}

export default PunchCardStamp