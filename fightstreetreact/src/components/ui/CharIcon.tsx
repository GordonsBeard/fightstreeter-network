import { characterCardImage } from "../../utils";

interface Props {
    selected_char: string;
    style: React.CSSProperties;
}

const CharIcon = ({ selected_char, style }: Props) => {
    const characterName = selected_char ? selected_char : "Random";
    return (
        <img src={characterCardImage.get(characterName)}
            style={style}
            className="rounded-start" />
    )
}

export default CharIcon