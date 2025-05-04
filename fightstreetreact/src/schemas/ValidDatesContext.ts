import { createContext } from "react";
import ValidDatesSchema from "./ValidDatesSchema";
import axios from "axios";


async function fetchValidDates() {
    const response = await axios.get<ValidDatesSchema>("http://localhost:5000/leaderboards/dates");
    const dates = response.data;
    return dates;
}

export const DatesContext = createContext<ValidDatesSchema>(await fetchValidDates());