import React from "react";

import {NumberInput} from "hds-react";

import {CommonFormInputFieldProps} from "./FormInputField";

interface FormNumberInputFieldProps extends Omit<CommonFormInputFieldProps, "value"> {
    value: number;
    fractionDigits?: number;
    unit?: string;
}

export default function FormNumberInputField({
    setFieldValue,
    unit,
    fractionDigits,
    required,
    ...rest
}: FormNumberInputFieldProps): JSX.Element {
    return (
        <div className={`input-field input-field--number${required ? " input-field--required" : "foo"}`}>
            <NumberInput
                onChange={(e) =>
                    setFieldValue(Number(Number(e.target.value).toFixed(fractionDigits ? fractionDigits : 0)))
                }
                unit={unit ? unit : ""}
                required={required}
                {...rest}
            />
        </div>
    );
}
