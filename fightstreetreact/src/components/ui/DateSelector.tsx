import { useContext } from 'react'
import { DatesContext } from '../../schemas/ValidDatesContext';

interface Props {
    dateValue: string;
    handleDateChange: (value: string) => void;
}

function DateSelector({ handleDateChange }: Props) {
    const validDates = useContext(DatesContext);
    const punchCardDates = validDates.dates

    return (
        <div className="p-1 m-2 d-flex justify-content-around align-items-center">
            <div>
                <a className="icon-link" href="#">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" className="bi">
                        <path fillRule="evenodd" d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8" />
                    </svg>
                    Previous
                </a>
            </div>
            <select className="form-select m-2" aria-label="Date selector" onChange={e => handleDateChange(e.currentTarget.value)}>
                {validDates &&
                    punchCardDates.map((date: string) => (
                        <option value={date} key={date}>{date}</option>
                    ))};
            </select>
            <div>
                <a className="icon-link" href="#">
                    Next
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" className="bi">
                        <path fillRule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8" />
                    </svg>
                </a>
            </div>

        </div>
    )
}

export default DateSelector