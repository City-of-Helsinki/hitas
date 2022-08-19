import React from "react";

import {format, parse} from "date-fns";
import {DateInput} from "hds-react";

import {CommonFormInputFieldProps} from "./FormInputField";

interface FormDateInputFieldProps extends CommonFormInputFieldProps {
    setIsInvalid: (value) => void;
}

export default function FormDateInputField({
    value,
    setFieldValue,
    setIsInvalid,
    required,
    ...rest
}: FormDateInputFieldProps): JSX.Element {
    // Display the date in 'HDS date format' to the user, but internally keep the date stored in a format which
    // doesn't need to be converted before sending it to the API

    const hdsFormat = "dd.MM.yyyy";
    const apiFormat = "yyyy-MM-dd";

    const getValue = (): string => {
        // Try to convert Hitas API format to HDS date format
        try {
            return format(parse(value, apiFormat, new Date()), hdsFormat);
        } catch {
            return value;
        }
    };

    const handleOnChange = (newValue: string, valueAsDate: Date) => {
        // Try to convert HDS date to Hitas API date

        // Do not format the date if the year is obviously incomplete
        if (valueAsDate.getFullYear().toString().length < 4) {
            setFieldValue(newValue);
            if (newValue || required) {
                setIsInvalid(true);
            } else if (!newValue) {
                setIsInvalid(false);
            }
            return;
        }

        try {
            const convertedValue = format(valueAsDate, apiFormat);
            setFieldValue(convertedValue);
            setIsInvalid(false);
        } catch {
            setFieldValue(newValue);
            setIsInvalid(true);
        }
    };

    return (
        <DateInput
            value={(() => getValue())()}
            onChange={handleOnChange}
            language={"fi"}
            disableConfirmation={true}
            required={required}
            {...rest}
        />
    );
}
