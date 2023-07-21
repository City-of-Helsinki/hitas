import {Button} from "hds-react";
import React from "react";
import {useFieldArray, useForm, useFormContext} from "react-hook-form";
import {Link} from "react-router-dom";
import {Heading, QueryStateHandler} from "../../../common/components";
import {FormProviderForm, SelectInput} from "../../../common/components/forms";
import {useGetAvailablePostalCodesQuery} from "../../../common/services";
import {today} from "../../../common/utils";

type NewPostalCodes = {
    skipped: {
        missingCode: string;
        replacementCode1: string | null;
        replacementCode2: string | null;
    }[];
};

function ThirtyYearSkippedListItem({postalCode, companies, postalCodeOptionSet, index}): React.JSX.Element {
    const formObject = useFormContext();

    const options: {label: string; value: string}[] = [];
    postalCodeOptionSet.forEach((option) => {
        options.push({
            label: `${option.postal_code} (${option.price_by_area} €/m², alue: ${option.cost_area})`,
            value: option.postal_code,
        });
    });

    return (
        <li
            className="results-list__item"
            key={postalCode}
        >
            <div>
                <h2>{postalCode}</h2>
                <ul>
                    <li>{companies.length > 1 ? "Yhtiöt:" : "Yhtiö:"} </li>
                    {companies.map((company) => (
                        <li key={company.display_name}>
                            <Link
                                target="_blank"
                                rel="noopener noreferrer"
                                to={`/housing-companies/${company.id}`}
                            >
                                {company.display_name}
                            </Link>
                        </li>
                    ))}
                </ul>
            </div>
            <div className="inputs">
                <SelectInput
                    label="Korvaava postinumero"
                    name={`skipped.${index}.replacementCode1`}
                    options={options}
                    tooltipText="Puolet keskiarvosta, joka korvaa puuttuvan postinumeroalueen hinnan."
                    setDirectValue
                    required
                />
                <SelectInput
                    label="Korvaava postinumero"
                    name={`skipped.${index}.replacementCode2`}
                    options={options.filter(
                        (option) => option.value !== formObject.getValues(`skipped.${index}.replacementCode1`)
                    )}
                    tooltipText="Toinen korvaava postinumero on valittavissa vasta kun olet valinnut ensimmäisen puolikkaan."
                    disabled={formObject.getValues(`skipped.${index}.replacementCode1`) === null}
                    setDirectValue
                    required
                />
            </div>
        </li>
    );
}

const ThirtyYearSkippedList = ({companies, calculationDate, reCalculateFn}) => {
    // If in Test mode, use today's date as the calculation date
    const validCalculationDate = isNaN(Number(calculationDate.substring(0, 4))) ? today() : calculationDate;

    const {
        data: codes,
        error,
        isLoading,
    } = useGetAvailablePostalCodesQuery({
        calculation_date: validCalculationDate,
    });

    const skippedPostalCodes = {};
    // If there are skipped companies, group them by postal code
    if (companies && companies.length > 0) {
        companies.forEach(
            (company) =>
                (skippedPostalCodes[company.address.postal_code] =
                    skippedPostalCodes[company.address.postal_code] !== undefined
                        ? [...skippedPostalCodes[company.address.postal_code], company]
                        : [company])
        );
    }

    const initialValues: object[] = [];
    Object.entries(skippedPostalCodes).forEach((code) =>
        initialValues.push({missingCode: code[0], replacementCode1: null, replacementCode2: null})
    );
    const formObject = useForm<NewPostalCodes>({
        defaultValues: {skipped: initialValues},
        mode: "onBlur",
    });
    const {control, watch} = formObject;
    useFieldArray({name: "skipped", control});

    let skippedCheck = 0;
    watch("skipped").forEach((item) => {
        if (item.replacementCode1 === null || item.replacementCode2 === null) skippedCheck++;
    });

    return (
        <>
            <Heading type="body">Vertailu ei onnistunut</Heading>
            <p>
                Vertailua ei voitu suorittaa, koska seuraavilta postinumeroalueilta puuttuu keskineliöhinnat.
                <br />
                Ole hyvä ja valitse kutakin kohti kaksi korvaavaa postinumeroaluetta, joiden keskiarvoa käytetään
                vertailussa puuttuvan keskineliöhinnan sijaan.
            </p>
            <QueryStateHandler
                data={codes}
                error={error}
                isLoading={isLoading}
            >
                <FormProviderForm
                    formObject={formObject}
                    onSubmit={reCalculateFn}
                    className="companies companies--skipped"
                >
                    <div className="list">
                        <ul className="results-list">
                            {Object.entries(skippedPostalCodes).map(([key, value], index) => (
                                <ThirtyYearSkippedListItem
                                    key={key}
                                    postalCode={key}
                                    companies={value}
                                    postalCodeOptionSet={codes}
                                    index={index}
                                />
                            ))}
                        </ul>
                    </div>
                    <div className="row row--buttons">
                        <Button
                            theme="black"
                            type="submit"
                            disabled={skippedCheck !== 0}
                        >
                            Suorita vertailu korvaavin postinumeroin
                        </Button>
                    </div>
                </FormProviderForm>
            </QueryStateHandler>
        </>
    );
};

export default ThirtyYearSkippedList;
