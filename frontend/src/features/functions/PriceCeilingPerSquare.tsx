import {Button} from "hds-react";
import {useState} from "react";

import {
    useCalculatePriceCeilingMutation,
    useGetIndicesQuery,
    useGetPriceCeilingCalculationDataQuery,
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
                        year={item.year}
                        value={item.value}
                    />
                ))}
            </ul>
        </div>
    );
};

const ListItem = ({month, year, value}) => {
    return (
        <li className="results-list__item">
            <div className="period">
                {month}
                {years[new Date().getFullYear() - year]?.label}
            </div>
            <div className="value">{value}</div>
        </li>
    );
};

const PriceCeilingCalculationResult = ({data, currentMonth}) => {
    const {
        data: calculationData,
        error,
        isLoading,
    } = useGetPriceCeilingCalculationDataQuery({calculationMonth: currentMonth});
    return (
        <QueryStateHandler
            data={calculationData}
            error={error}
            isLoading={isLoading}
        >
            <span>Tälle neljännekselle on laskettu rajaneliöhinta:</span>
            <span>{data.contents[0].value}</span>
        </QueryStateHandler>
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
                    <span>Tälle neljännekselle on laskettu rajaneliöhinta:</span>
                    <span>{data.contents[0].value}</span>
                    <PriceCeilingCalculationResult
                        data={data}
                        currentMonth={currentMonth}
                    />
                    <CalculateButton />
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
    // FIXME: use today().slice(0, 7) for the current Month, the +3 is a hack for testing
    const currentMonth = new Date().getFullYear() + "-" + ("0" + (new Date().getMonth() + 1)).slice(-2);
    const [filterParams, setFilterParams] = useState({year: new Date().getFullYear().toString()});
    const {data, error, isLoading} = useGetIndicesQuery({
        indexType: "surface-area-price-ceiling",
        params: {...filterParams, limit: 12, page: 1},
    });
    console.log(data?.contents[0].month, currentMonth, today().slice(0, 7));

    return (
        <div className="view--functions__price-ceiling-per-square">
            <Heading type="body">Rajaneliöhinnan laskenta</Heading>
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
