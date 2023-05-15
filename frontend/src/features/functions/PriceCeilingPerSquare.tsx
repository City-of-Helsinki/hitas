import {Button, LoadingSpinner} from "hds-react";
import {useState} from "react";
import {useForm} from "react-hook-form";

import {hitasQuarters} from "../../common/schemas";

import {Heading} from "../../common/components";
import {Select} from "../../common/components/form";

export const years = Array.from({length: 34}, (_, index) => {
    const year = 2023 - index;
    return {
        value: year.toString(),
        label: year.toString(),
    };
});

const PriceCeilingPerSquare = () => {
    const [isLoading, setIsLoading] = useState(false);
    const formObject = useForm({
        defaultValues: {year: years[1], quarter: hitasQuarters[0]},
        mode: "all",
    });
    const CalculateButton = () => (
        <Button
            className="calculate-button"
            theme="black"
            variant="secondary"
            onClick={() => setIsLoading(!isLoading)}
            disabled={isLoading}
        >
            <span>Laske{isLoading && "taan..."}</span>
            {isLoading && (
                <div className="spinner-wrap">
                    <LoadingSpinner />
                </div>
            )}
        </Button>
    );
    const ListItem = ({quarter, year, value}) => {
        return (
            <li className="results-list__item">
                <div className="period">
                    {hitasQuarters[quarter].label}
                    {years[new Date().getFullYear() - year].label}
                </div>
                <div className="value">{value !== undefined ? value : <CalculateButton />}</div>
            </li>
        );
    };
    return (
        <div className="view--functions__price-ceiling-per-square">
            <Heading type="body">Rajaneliöhinnan laskenta</Heading>
            <div className="list">
                <div className="list-headers">
                    <div className="period">Ajanjakso</div>
                    <div className="value">Rajaneliöhinta (€)</div>
                </div>
                <ul className="results-list">
                    <ListItem
                        quarter={0}
                        year={2023}
                        value={undefined}
                    />
                    <ListItem
                        quarter={3}
                        year={2022}
                        value="123"
                    />
                    <ListItem
                        quarter={2}
                        year={2022}
                        value="123"
                    />
                </ul>
            </div>
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
        </div>
    );
};

export default PriceCeilingPerSquare;
