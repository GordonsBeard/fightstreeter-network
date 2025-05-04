import { createContext } from "react";
import ValidPhasesSchema from "./ValidPhasesSchema";
import axios from "axios";

async function fetchValidPhases() {
    const response = await axios.get<ValidPhasesSchema>("http://localhost:5000/leaderboards/phases");
    const dates = response.data;
    return dates;
}

export const PhasesContext = createContext<ValidPhasesSchema>(await fetchValidPhases());