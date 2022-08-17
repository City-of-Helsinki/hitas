import React from "react";

import {TextInput} from "hds-react";

import {CommonFormInputFieldProps} from "./FormInputField";

interface FormPostalCodeInputFieldProps extends CommonFormInputFieldProps {
    setIsInvalid: (value) => void;
}

export default function FormPostalCodeInputField({
    setFieldValue,
    setIsInvalid,
    required,
    ...rest
}: FormPostalCodeInputFieldProps): JSX.Element {
    const handleOnChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        // Remove all non-number characters from the value
        setFieldValue(e.target.value.replace(/\D/g, ""));
    };

    const handleOnBlur = (e: React.ChangeEvent<HTMLInputElement>) => {
        if ((required && e.target.value.length !== 5) || (!required && !e.target.value.length)) {
            setIsInvalid(true);
        }
    };

    return (
        <TextInput
            onChange={handleOnChange}
            onBlur={handleOnBlur}
            onFocus={() => setIsInvalid(false)}
            maxLength={5}
            required={required}
            {...rest}
        />
    );
}
