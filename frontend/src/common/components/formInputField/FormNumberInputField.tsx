import React from "react";

import {NumberInput} from "hds-react";

import {CommonFormInputFieldProps} from "./FormInputField";

interface FormNumberInputFieldProps extends Omit<CommonFormInputFieldProps, "value"> {
    value: number;
    unit?: string;
}

export default function FormNumberInputField({setFieldValue, unit, ...rest}: FormNumberInputFieldProps): JSX.Element {
    const fractionDigits = unit === "€" ? 2 : 0;
    return (
        <NumberInput
            onChange={(e) => setFieldValue(Number(Number(e.target.value).toFixed(fractionDigits)))}
            unit={unit ? unit : ""}
            {...rest}
        />
    );
}
