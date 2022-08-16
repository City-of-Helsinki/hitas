import React, {useState} from "react";

import {TextInput} from "hds-react";

interface FilterTextInputFieldProps {
    label: string;
    filterFieldName: string;
    filterParams: {string: string | number};
    setFilterParams: (object) => void;
}

export default function FilterTextInputField({
    label,
    filterFieldName,
    filterParams,
    setFilterParams,
}: FilterTextInputFieldProps): JSX.Element {
    const MIN_LENGTH = 3;
    const [isInvalid, setIsInvalid] = useState(false);

    const handleOnChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        const filters = {...filterParams};

        // Update filter value or clear it when field is cleared or value is too short
        if (filters[filterFieldName] && (!value || value.length < MIN_LENGTH)) {
            delete filters[filterFieldName];
            setFilterParams(filters);
            return;
        } else if (e.target.value.length >= MIN_LENGTH) {
            filters[filterFieldName] = e.target.value;
            setFilterParams(filters);
        }
    };

    const handleOnBlur = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.value.length && e.target.value.length < MIN_LENGTH) {
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
        />
    );
}
