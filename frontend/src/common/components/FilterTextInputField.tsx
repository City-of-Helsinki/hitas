import React, {useState} from "react";

import {TextInput} from "hds-react";

interface FilterTextInputFieldProps {
    label: string;
    filterFieldName: string;
    filterParams: object;
    setFilterParams: (object) => void;
    minLength?: number;
    maxLength?: number;
    defaultValue?: string;
    required?: boolean;
    tooltipText?: string;
}

export default function FilterTextInputField({
    label,
    filterFieldName,
    filterParams,
    setFilterParams,
    minLength = 3,
    maxLength,
    ...rest
}: FilterTextInputFieldProps): JSX.Element {
    const [isInvalid, setIsInvalid] = useState(false);

    const handleOnChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        const filters = {...filterParams};

        // Update filter value or clear it when field is cleared or value is too short
        if (filters[filterFieldName] && (!value || value.length < minLength)) {
            delete filters[filterFieldName];
            setFilterParams(filters);
            return;
        } else if (e.target.value.length >= minLength) {
            filters[filterFieldName] = e.target.value;
            setFilterParams(filters);
        }
    };

    const handleOnBlur = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.value.length && e.target.value.length < minLength) {
            setIsInvalid(true);
        }
    };

    return (
        <TextInput
            id={`filter__${filterFieldName}`}
            label={label}
            onChange={handleOnChange}
            onBlur={handleOnBlur}
            onFocus={() => setIsInvalid(false)}
            invalid={isInvalid}
            maxLength={maxLength}
            {...rest}
        />
    );
}
