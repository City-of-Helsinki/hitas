import {Option, Select} from "hds-react";
import React, {useCallback, useState} from "react";

interface FilterComboboxProps {
    label: string;
    options: Partial<Option>[];
    defaultOption?: Partial<Option>;
    filterFieldName: string;
    filterParams: object;
    setFilterParams: (object) => void;
}

export default function FilterSelectField({
    label,
    options,
    defaultOption,
    filterFieldName,
    filterParams,
    setFilterParams,
}: FilterComboboxProps): React.JSX.Element {
    if (defaultOption === undefined) {
        defaultOption = {
            label: options.find((o) => o.value === filterParams[filterFieldName])?.label ?? "",
            value: filterParams[filterFieldName],
        };
    }

    const [value, setValue] = useState<Partial<Option>[]>(defaultOption ? [defaultOption] : []);

    const onSelectionChange = useCallback((selectedOptions: Option[]) => {
        const selected = selectedOptions[0];
        // Update set filter, or remove key if filter is cleared
        const filters = {...filterParams};
        if (selected) {
            filters[filterFieldName] = selected.value;
        } else {
            delete filters[filterFieldName];
        }
        setFilterParams(filters);
        setValue(selectedOptions);
    }, []);

    return (
        <Select
            id={`filter__${filterFieldName}`}
            texts={{
                label,
                placeholder: "",
            }}
            options={options}
            value={value}
            onChange={onSelectionChange}
            clearable
        />
    );
}
