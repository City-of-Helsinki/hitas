import React from "react";

import {NumberInput} from "hds-react";

import {CommonFormInputFieldProps} from "./FormInputField";

interface FormNumberInputFieldProps extends Omit<CommonFormInputFieldProps, "value"> {
    value: number;
    unit?: string;
}

export default function FormNumberInputField({setFieldValue, unit, ...rest}: FormNumberInputFieldProps): JSX.Element {
    return (
        <NumberInput
            onChange={(e) => setFieldValue(Number(Number(e.target.value).toFixed(2)))}
            unit={unit ? unit : ""}
            {...rest}
        />
    );
}
