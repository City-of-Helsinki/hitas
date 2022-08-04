import React, {useState} from "react";

import {TextInput} from "hds-react";

interface IFilterPostalCodeInput {
    label: string;
    filterFieldName: string;
    filterParams: {string: string | number};
    setFilterParams: (object) => void;
}

export default function FilterPostalCodeInput({
    label,
    filterFieldName,
    filterParams,
    setFilterParams,
}: IFilterPostalCodeInput) {
    const [inputValue, setInputValue] = useState("");
    const [isInvalid, setIsInvalid] = useState(false);

    const handleOnChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value.replace(/\D/g, "");
        setInputValue(value);

        // Check if value is changed. We don't want to trigger when a letter is inputted
        if (inputValue !== value) {
            const filters = {...filterParams};
            // Filter is set, and should be cleared
            if (filters[filterFieldName] && (!value || value.length < 5)) {
                delete filters[filterFieldName];
                setFilterParams(filters);
                return;
            }
            // Filter should be set
            else if (value.length === 5) {
                filters[filterFieldName] = value;
                setFilterParams(filters);
            }
        }
    };

    const handleOnBlur = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.value.length && e.target.value.length !== 5) {
            setIsInvalid(true);
        }
    };

    return (
        <TextInput
            id={`filter__${filterFieldName}`}
            label={label}
            value={inputValue}
            maxLength={5}
            onChange={handleOnChange}
            onBlur={handleOnBlur}
            onFocus={() => setIsInvalid(false)}
            invalid={isInvalid}
        />
    );
}
