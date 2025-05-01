import { createContext } from "react";
import ValidDates from "./ValidDates";
import axios from "axios";


async function fetchDateSelector() {
    const response = await axios.get<ValidDates>("http://localhost:5000/leaderboards/dates");
    const dates = response.data;
    return dates;
}

export const DatesContext = createContext<ValidDates>(await fetchDateSelector());