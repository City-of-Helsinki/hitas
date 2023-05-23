import {Select} from "hds-react";

interface FilterComboboxProps {
    label: string;
    options: {label: string; value: string}[];
    filterFieldName: string;
    filterParams: object;
    setFilterParams: (object) => void;
}

export default function FilterSelectField({
    label,
    options,
    filterFieldName,
    filterParams,
    setFilterParams,
}: FilterComboboxProps): JSX.Element {
    const onSelectionChange = (value: {label: string; value: string}) => {
        // Update set filter, or remove key if filter is cleared
        const filters = {...filterParams};
        if (!value) {
            delete filters[filterFieldName];
            setFilterParams(filters);
            return;
        }
        filters[filterFieldName] = value.value;
        setFilterParams(filters);
    };

    return (
        <Select
            id={`filter__${filterFieldName}`}
            label={label}
            options={options}
            onChange={onSelectionChange}
            clearable
        />
    );
}
