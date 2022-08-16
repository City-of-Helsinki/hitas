import React, {useEffect, useState} from "react";

import {Combobox} from "hds-react";

interface FilterRelatedModelComboboxFieldProps {
    label: string;
    queryFunction;
    labelField: string;
    filterFieldName: string;
    filterParams: {string: string | number};
    setFilterParams: (object) => void;
}

export default function FilterRelatedModelComboboxField({
    label,
    queryFunction,
    labelField,
    filterFieldName,
    filterParams,
    setFilterParams,
    const LOADING_OPTION = {label: "Loading..."};
    const [options, setOptions] = useState([LOADING_OPTION]);
}: FilterRelatedModelComboboxFieldProps): JSX.Element {
    const [skip, setSkip] = useState(true);

    const {data} = queryFunction({}, {skip: skip});

    useEffect(() => {
        if (data && data?.contents) {
            setOptions(
                data.contents.map((o) => {
                    return {label: o[labelField]};
                })
            );
        }
    }, [data]);

    const onFocus = () => {
        // Options should be loaded only after field is focused to reduce unnecessary api queries
        setSkip(false);
    };

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
            isOptionDisabled={(option, index: number) => index === 0 && option.label === LOADING_OPTION.label}
            toggleButtonAriaLabel="Toggle menu"
            onChange={onSelectionChange}
            onFocus={onFocus}
            clearable
        />
    );
}
