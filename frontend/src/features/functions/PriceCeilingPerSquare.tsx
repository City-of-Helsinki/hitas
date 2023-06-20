import {Button} from "hds-react";
import {useState} from "react";
import {useForm} from "react-hook-form";

import {hitasQuarters} from "../../common/schemas";

import {useGetIndicesQuery} from "../../app/services";
import {FilterTextInputField, Heading, QueryStateHandler} from "../../common/components";
import {Select} from "../../common/components/form";

export const years = Array.from({length: 34}, (_, index) => {
    const year = 2023 - index;
    return {
        value: year.toString(),
        label: year.toString(),
    };
});

const LoadedPriceCeilingPerSquareResultsList = ({data}) => {
    console.log(data.contents);
    return (
        <div className="results">
            <div className="list-headers">
                <div className="list-header period">Ajanjakso</div>
                <div className="list-header value">Rajaneliöhinta (€)</div>
            </div>
            <ul className="results-list">
                {data?.contents.map((item) => (
                    <ListItem
                        key={`${item.year}-${item.quarter}`}
                        month={item.month}
                        year={item.year}
                        value={item.value}
                    />
                ))}
            </ul>
        </div>
    );
};

const CalculateButton = () => (
    <Button
        className="calculate-button"
        theme="black"
        variant="secondary"
        onClick={() => console.log("Calculating")}
    >
        <span>Laske</span>
    </Button>
);

const ListItem = ({month, year, value}) => {
    console.log(month);
    return (
        <li className="results-list__item">
            <div className="period">
                {month}
                {years[new Date().getFullYear() - year]?.label}
            </div>
            <div className="value">{value ?? <CalculateButton />}</div>
        </li>
    );
};

const PriceCeilingPerSquare = () => {
    const [filterParams, setFilterParams] = useState({year: "2023"});
    const {data, error, isLoading} = useGetIndicesQuery({
        indexType: "surface-area-price-ceiling",
        params: {...filterParams, limit: 12, page: 1},
    });
    const formObject = useForm({
        defaultValues: {year: years[1], quarter: hitasQuarters[0]},
        mode: "all",
    });

    return (
        <div className="view--functions__price-ceiling-per-square">
            <Heading type="body">Rajaneliöhinnan laskenta</Heading>
            <form>
                <div>
                    <Select
                        label="Vuosi"
                        options={years}
                        name="year"
                        formObject={formObject}
                        defaultValue={years[0]}
                    />
                    <Select
                        label="Ajanjakso"
                        options={hitasQuarters}
                        name="period"
                        formObject={formObject}
                        defaultValue={hitasQuarters[0]}
                    />
                    <CalculateButton />
                </div>
            </form>
            <Heading type="body">Edelliset rajaneliöhinnat</Heading>
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
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
