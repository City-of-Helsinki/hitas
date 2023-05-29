import {Link} from "react-router-dom";
import {Select} from "../../../common/components/form";

export default function ThirtyYearSkippedListItem({
    postalCode,
    companies,
    postalCodeOptionSet,
    formObject,
    index,
}): JSX.Element {
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
                <Select
                    label="Korvaava postinumero"
                    tooltipText="Puolet keskiarvosta, joka korvaa puuttuvan postinumeroalueen hinnan."
                    options={options}
                    name={`skipped.${index}.replacementCode1`}
                    formObject={formObject}
                    setDirectValue={true}
                    required
                />
                <Select
                    label="Korvaava postinumero"
                    tooltipText="Toinen korvaava postinumero on valittavissa vasta kun olet valinnut ensimmäisen puolikkaan."
                    options={options.filter(
                        (option) => option.value !== formObject.getValues(`skipped.${index}.replacementCode1`)
                    )}
                    name={`skipped.${index}.replacementCode2`}
                    formObject={formObject}
                    setDirectValue={true}
                    disabled={formObject.getValues(`skipped.${index}.replacementCode1`) === null}
                    required
                />
            </div>
        </li>
    );
}