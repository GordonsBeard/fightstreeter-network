interface Props {
    date: string;
}

function DateSelector({ date }: Props) {
    return (
        <div className="p-1 d-flex justify-content-around">
            <div>
                <a className="icon-link" href="#">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" className="bi">
                        <path fill-rule="evenodd" d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8" />
                    </svg>
                    Previous
                </a>
            </div>
            <div><input type="date" value={date} /></div>
            <div>
                <a className="icon-link" href="#">
                    Next
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" className="bi">
                        <path fill-rule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8" />
                    </svg>
                </a>
            </div>

        </div>
    )
}

export default DateSelector