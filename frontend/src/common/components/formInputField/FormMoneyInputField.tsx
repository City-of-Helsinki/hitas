import React from "react";

import {NumberInput} from "hds-react";

import {CommonFormInputFieldProps} from "./FormInputField";

interface FormMoneyInputFieldProps extends Omit<CommonFormInputFieldProps, "value"> {
    value: number;
}

export default function FormMoneyInputField({setFieldValue, ...rest}: FormMoneyInputFieldProps): JSX.Element {
    return (
        <NumberInput
            onChange={(e) => setFieldValue(Number(Number(e.target.value).toFixed(2)))}
            unit="€"
            {...rest}
        />
    );
}
