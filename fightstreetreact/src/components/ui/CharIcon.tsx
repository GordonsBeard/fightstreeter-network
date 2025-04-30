import card_aki from "../../assets/img/card/card_aki.jpg"
import card_blanka from "../../assets/img/card/card_blanka.jpg"
import card_cammy from "../../assets/img/card/card_cammy.jpg"
import card_chunli from "../../assets/img/card/card_chunli.jpg"
import card_deejay from "../../assets/img/card/card_deejay.jpg"
import card_dhalsim from "../../assets/img/card/card_dhalsim.jpg"
import card_ed from "../../assets/img/card/card_ed.jpg"
import card_gouki from "../../assets/img/card/card_gouki.jpg"
import card_guile from "../../assets/img/card/card_guile.jpg"
import card_honda from "../../assets/img/card/card_honda.jpg"
import card_jamie from "../../assets/img/card/card_jamie.jpg"
import card_jp from "../../assets/img/card/card_jp.jpg"
import card_juri from "../../assets/img/card/card_juri.jpg"
import card_ken from "../../assets/img/card/card_ken.jpg"
import card_kimberly from "../../assets/img/card/card_kimberly.jpg"
import card_lily from "../../assets/img/card/card_lily.jpg"
import card_luke from "../../assets/img/card/card_luke.jpg"
import card_mai from "../../assets/img/card/card_mai.jpg"
import card_manon from "../../assets/img/card/card_manon.jpg"
import card_marisa from "../../assets/img/card/card_marisa.jpg"
import card_rashid from "../../assets/img/card/card_rashid.jpg"
import card_ryu from "../../assets/img/card/card_ryu.jpg"
import card_terry from "../../assets/img/card/card_terry.jpg"
import card_vega from "../../assets/img/card/card_vega.jpg"
import card_zangief from "../../assets/img/card/card_zangief.jpg"
import card_random from "../../assets/img/card/card_random.jpg"

const char_cards: Map<string, string> = new Map([
    ["A.K.I.", card_aki],
    ["Blanka", card_blanka],
    ["Cammy", card_cammy],
    ["Chun-Li", card_chunli],
    ["Dee Jay", card_deejay],
    ["Dhalsim", card_dhalsim],
    ["Ed", card_ed],
    ["Akuma", card_gouki],
    ["Guile", card_guile],
    ["E. Honda", card_honda],
    ["Jamie", card_jamie],
    ["JP", card_jp],
    ["Juri", card_juri],
    ["Ken", card_ken],
    ["Kimberly", card_kimberly],
    ["Lily", card_lily],
    ["Luke", card_luke],
    ["Mai", card_mai],
    ["Manon", card_manon],
    ["Marisa", card_marisa],
    ["Rashid", card_rashid],
    ["Ryu", card_ryu],
    ["Terry", card_terry],
    ["M. Bison", card_vega],
    ["Zangief", card_zangief],
    ["Random", card_random],
]);

interface Props {
    selected_char?: string;
    style: React.CSSProperties;
}

const CharIcon = ({ selected_char, style }: Props) => {
    const characterName = selected_char ? selected_char : "Random";
    return (
        <img src={char_cards.get(characterName)}
            style={style}
            className="rounded-start" />
    )
}

export default CharIcon