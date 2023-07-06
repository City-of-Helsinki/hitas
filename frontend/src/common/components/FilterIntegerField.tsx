import React, {useState} from "react";

import {TextInput} from "hds-react";

interface FilterIntegerFieldProps {
    label: string;
    minLength: number;
    maxLength: number;
    filterFieldName: string;
    filterParams: object;
    setFilterParams: (object) => void;
}

export default function FilterIntegerField({
    label,
    minLength, // The minimum length at which the filter is applied
    maxLength,
    filterFieldName,
    filterParams,
    setFilterParams,
}: FilterIntegerFieldProps): React.JSX.Element {
    const [inputValue, setInputValue] = useState("");
    const [isInvalid, setIsInvalid] = useState(false);

    const handleOnChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value.replace(/\D/g, "");
        setInputValue(value);

        // Check if value is changed. We don't want to trigger when a letter is inputted
        if (inputValue !== value) {
            const filters = {...filterParams};
            // Filter is set, and should be cleared
            if (filters[filterFieldName] && (!value || value.length < minLength)) {
                delete filters[filterFieldName];
                setFilterParams(filters);
                return;
            }
            // Filter should be set
            else if (value.length >= minLength) {
                filters[filterFieldName] = value;
                setFilterParams(filters);
            }
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
            value={inputValue}
            maxLength={maxLength}
            onChange={handleOnChange}
            onBlur={handleOnBlur}
            onFocus={() => setIsInvalid(false)}
            invalid={isInvalid}
        />
    );
}
