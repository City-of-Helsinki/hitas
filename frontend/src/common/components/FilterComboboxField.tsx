import React from "react";

import {Combobox} from "hds-react";

interface IFilterCombobox {
    label: string;
    options: {label: string}[];
    filterFieldName: string;
    filterParams: {string: string | number};
    setFilterParams: (object) => void;
}

export default function FilterComboboxField({
    label,
    options,
    filterFieldName,
    filterParams,
    setFilterParams,
}: IFilterCombobox) {
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
