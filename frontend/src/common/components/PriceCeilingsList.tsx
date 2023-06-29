import {useState} from "react";
import {useGetIndicesQuery} from "../../app/services";
import {getHitasQuarter} from "../utils";
import DownloadButton from "./DownloadButton";
import {Divider, FilterTextInputField, QueryStateHandler} from "./index";

const LoadedPriceCeilingPerSquareResultsList = ({data, callbackFn}) => {
    return (
        <div className="results">
            <div className="list-headers">
                <div className="list-header period">Vuosineljännes</div>
                <div className="list-header value">{callbackFn ? "Raportti" : "Rajaneliöhinta (€/m²)"}</div>
            </div>
            <ul className="results-list">
                {data?.contents.map((item) => (
                    <ListItem
                        key={item.month}
                        month={item.month}
                        value={item.value}
                        callbackFn={callbackFn ? () => callbackFn && callbackFn(item.month + "-01") : undefined}
                    />
                ))}
            </ul>
        </div>
    );
};

const ListItem = ({month, value, callbackFn}) => {
    // the month is in the format YYYY-MM
    const [yearString, monthString] = month.split("-");
    let timePeriod = month;
    switch (monthString) {
        case "01":
            // add the previous year in the start date for january, as its quarter begins in the previous year
            timePeriod = `${getHitasQuarter(month).label.split(" ")[0]}${Number(yearString) - 1} - ${
                getHitasQuarter(month).label.split("-")[1]
            }${yearString}`;
            break;
        case "02":
        case "05":
        case "08":
            // for the months which start a new quarter, simply add the year to the end of the quarter label
            timePeriod = `${getHitasQuarter(month).label}${yearString}`;
            break;
        case "11":
            // add the next year in the end date for the last quarter, as the quarter ends in the next year
            timePeriod = `${getHitasQuarter(month).label.split(" ")[0]}${yearString} - ${
                getHitasQuarter(month).label.split("-")[1]
            }${Number(yearString) + 1}`;
            break;
        default:
            // for the months which are not the start of a new quarter (or year), do not display the value
            return <> </>;
    }
    return (
        <li className="results-list__item">
            <div className="period">{timePeriod}</div>
            {callbackFn !== undefined ? (
                <DownloadButton
                    onClick={callbackFn}
                    buttonText="Lataa raportti"
                    size="small"
                />
            ) : (
                <div className="value">{value}</div>
            )}
        </li>
    );
};

const PriceCeilingsList = ({callbackFn}: {callbackFn?: (() => void) | boolean}) => {
    const [filterParams, setFilterParams] = useState({year: new Date().getFullYear().toString()});
    const {data, error, isLoading} = useGetIndicesQuery({
        indexType: "surface-area-price-ceiling",
        params: {...filterParams, limit: 12, page: 1},
    });
    return (
        <div className="price-ceiling-per-square-list">
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
                attemptedAction="Haetaan rajaneliöhintalistausta"
            >
                <Divider size="s" />
                <div className="price-ceiling-results">
                    <FilterTextInputField
                        label="Vuosi"
                        filterFieldName="year"
                        defaultValue={filterParams.year}
                        filterParams={filterParams}
                        setFilterParams={setFilterParams}
                        minLength={4}
                        maxLength={4}
                        tooltipText="Syötä vuosiluku nähdäksesi sille lasketut rajaneliöhintaraportit"
                        required
                    />
                    {filterParams.year ? (
                        <LoadedPriceCeilingPerSquareResultsList
                            data={data}
                            callbackFn={callbackFn}
                        />
                    ) : (
                        <></>
                    )}
                </div>
            </QueryStateHandler>
        </div>
    );
};

export default PriceCeilingsList;
