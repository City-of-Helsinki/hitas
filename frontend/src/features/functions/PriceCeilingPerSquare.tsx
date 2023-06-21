import {Button} from "hds-react";
import {useState} from "react";

import {
    downloadSurfaceAreaPriceCeilingResults,
    useCalculatePriceCeilingMutation,
    useGetIndicesQuery,
} from "../../app/services";
import {FilterTextInputField, Heading, QueryStateHandler} from "../../common/components";
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
                <div className="list-header period">Ajanjakso</div>
                <div className="list-header value">Rajaneliöhinta (€)</div>
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
    const year = month.slice(0, 4);
    let timePeriod;
    switch (month.slice(-2)) {
        case "01":
            timePeriod = `${getHitasQuarter(month).label.split(" ")[0]}${Number(year) - 1} - ${
                getHitasQuarter(month).label.split("-")[1]
            }${year}`;
            break;
        case "02":
        case "05":
        case "08":
            timePeriod = `${getHitasQuarter(month).label}${year}`;
            break;
        case "11":
            timePeriod = `${getHitasQuarter(month).label.split(" ")[0]}${year} - ${
                getHitasQuarter(month).label.split("-")[1]
            }${Number(year) + 1}`;
            break;
        default:
            return <></>;
    }
    return timePeriod !== undefined ? (
        <li className="results-list__item">
            <div className="period">{timePeriod}</div>
            <div className="value">{value}</div>
        </li>
    ) : (
        <></>
    );
};

const PriceCeilingCalculationSection = ({data, currentMonth}) => {
    const [calculatePriceCeiling] = useCalculatePriceCeilingMutation();
    const handleCalculateButton = () => {
        calculatePriceCeiling({
            data: {calculation_month: currentMonth},
        })
            .then((data) => {
                console.log(data);
                hdsToast.success("Rajahinnan laskenta onnistui");
            })
            .catch((e) => {
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
                            Rajaneliöhinta (<>{getHitasQuarter(currentMonth + "-01").label}</>)
                        </label>
                        <span>{data.contents[0].value}</span>
                    </div>
                    <Button
                        theme="black"
                        onClick={() => downloadSurfaceAreaPriceCeilingResults(currentMonth + "-01")}
                    >
                        Lataa laskentaraportti
                    </Button>
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
    const {data, error, isLoading} = useGetIndicesQuery({
        indexType: "surface-area-price-ceiling",
        params: {...filterParams, limit: 12, page: 1},
    });

    return (
        <div className="view--functions__price-ceiling-per-square">
            <Heading type="body">Nykyisen neljänneksen rajaneliöhinta</Heading>
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
                attemptedAction="Haetaan rajaneliöhintalistausta"
            >
                <PriceCeilingCalculationSection
                    data={data}
                    currentMonth={currentMonth}
                />
                <Heading type="sub">Edelliset rajaneliöhinnat</Heading>
                <LoadedPriceCeilingPerSquareResultsList data={data} />
            </QueryStateHandler>
            <div className="year-filter">
                <FilterTextInputField
                    label="Vuosi"
                    filterFieldName="year"
                    filterParams={filterParams}
                    setFilterParams={setFilterParams}
                    minLength={4}
                    maxLength={4}
                />
            </div>
        </div>
    );
};

export default PriceCeilingPerSquare;
