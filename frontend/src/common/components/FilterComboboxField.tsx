import {Combobox} from "hds-react";

interface FilterComboboxProps {
    label: string;
    options: {label: string}[];
    filterFieldName: string;
    filterParams: object;
    setFilterParams: (object) => void;
}

export default function FilterComboboxField({
    label,
    options,
    filterFieldName,
    filterParams,
    setFilterParams,
}: FilterComboboxProps): JSX.Element {
    const onSelectionChange = (value: {label: string}) => {
        // Update set filter, or remove key if filter is cleared
        const filters = {...filterParams};
        if (!value) {
            delete filters[filterFieldName];
            setFilterParams(filters);
            return;
        }
        filters[filterFieldName] = value.label;
        setFilterParams(filters);
    };

    return (
        <Combobox
            id={`filter__${filterFieldName}`}
            label={label}
            options={options}
            toggleButtonAriaLabel="Toggle menu"
            onChange={onSelectionChange}
            clearable
        />
    );
}
