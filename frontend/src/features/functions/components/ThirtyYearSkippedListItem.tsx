import React from "react";
import {useFormContext} from "react-hook-form";
import {Link} from "react-router-dom";
import {SelectInput} from "../../../common/components/forms";

export default function ThirtyYearSkippedListItem({
    postalCode,
    companies,
    postalCodeOptionSet,
    index,
}): React.JSX.Element {
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
