import {Button} from "hds-react";
import {useState} from "react";

import {
    downloadSurfaceAreaPriceCeilingResults,
    useCalculatePriceCeilingMutation,
    useGetIndicesQuery,
} from "../../app/services";
import {FilterTextInputField, Heading, QueryStateHandler} from "../../common/components";
import DownloadButton from "../../common/components/DownloadButton";
import {getHitasQuarter, hdsToast, today} from "../../common/utils";

export const years = Array.from({length: 34}, (_, index) => {
    const year = 2023 - index;
    return {
        value: year.toString(),
        label: year.toString(),
    };
});

const LoadedPriceCeilingPerSquareResultsList = ({data}) => {
    return (
        <div className="results">
            <div className="list-headers">
                <div className="list-header period">Vuosineljännes</div>
                <div className="list-header value">Rajaneliöhinta (€/m²)</div>
            </div>
            <ul className="results-list">
                {data?.contents.map((item) => (
                    <ListItem
                        key={item.month}
                        month={item.month}
                        value={item.value}
                    />
                ))}
            </ul>
        </div>
    );
};

const ListItem = ({month, value}) => {
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
            <div className="value">{value}</div>
        </li>
    );
};

const PriceCeilingCalculationSection = ({data, currentMonth}) => {
    const [calculatePriceCeiling] = useCalculatePriceCeilingMutation();
    const handleCalculateButton = () => {
        calculatePriceCeiling({
            data: {calculation_month: currentMonth},
        })
            .then(() => {
                hdsToast.success("Rajahinnan laskenta onnistui");
            })
            .catch((e) => {
                // eslint-disable-next-line no-console
                console.warn(e);
                hdsToast.error("Rajahinnan laskenta epäonnistui");
            });
    };
    const CalculateButton = () => (
        <Button
            className="calculate-button"
            theme="black"
            onClick={handleCalculateButton}
        >
            <span>Laske rajaneliöhinta</span>
        </Button>
    );

    return (
        <div className="price-ceiling-calculation">
            {data.contents.some((item) => item.month === currentMonth) ? (
                <>
                    <div className="price-ceiling-value">
                        <label>
                            Rajaneliöhinta (<>{getHitasQuarter().label}</>)
                        </label>
                        <span>{data.contents[0].value}</span>
                    </div>
                    <DownloadButton
                        downloadFn={() => downloadSurfaceAreaPriceCeilingResults(currentMonth + "-01")}
                        buttonText="Lataa laskentaraportti"
                    />
                </>
            ) : (
                <>
                    <p>Tälle neljännekselle ({getHitasQuarter().label}) ei vielä ole laskettu rajaneliöhintaa</p>
                    <CalculateButton />
                </>
            )}
        </div>
    );
};

const PriceCeilingPerSquare = () => {
    const currentMonth = today().slice(0, 7);
    const [filterParams, setFilterParams] = useState({year: new Date().getFullYear().toString()});
    const {
        data: currentCalculationData,
        error: currentCalculationError,
        isLoading: isCurrentCalculationLoading,
    } = useGetIndicesQuery({
        indexType: "surface-area-price-ceiling",
        params: {year: today().split("-")[0], limit: 12, page: 1},
    });
    const {data, error, isLoading} = useGetIndicesQuery({
        indexType: "surface-area-price-ceiling",
        params: {...filterParams, limit: 12, page: 1},
    });
    return (
        <div className="view--functions__price-ceiling-per-square">
            <Heading type="body">Rajaneliöhinnan laskenta</Heading>
            <QueryStateHandler
                data={currentCalculationData}
                error={currentCalculationError}
                isLoading={isCurrentCalculationLoading}
                attemptedAction="Haetaan rajaneliöhintalistausta (tarkistetaan onko nykyinen laskettu)"
            >
                <PriceCeilingCalculationSection
                    data={currentCalculationData}
                    currentMonth={currentMonth}
                />
            </QueryStateHandler>
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
                attemptedAction="Haetaan rajaneliöhintalistausta"
            >
                <Heading type="sub">Rajaneliöhinnat</Heading>
                <div className="price-ceiling-results">
                    <FilterTextInputField
                        label="Vuosi"
                        filterFieldName="year"
                        defaultValue={filterParams.year}
                        filterParams={filterParams}
                        setFilterParams={setFilterParams}
                        minLength={4}
                        maxLength={4}
                        required
                    />
                    {filterParams.year ? <LoadedPriceCeilingPerSquareResultsList data={data} /> : <></>}
                </div>
            </QueryStateHandler>
        </div>
    );
};

export default PriceCeilingPerSquare;
