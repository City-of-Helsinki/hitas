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
    const formatNumber = (v: string): number | null => {
        if (v === "") return null;
        return Number(Number().toFixed(fractionDigits ? fractionDigits : 0));
    };

    return (
        <div className={`input-field input-field--number${required ? " input-field--required" : "foo"}`}>
            <NumberInput
                onChange={(e) => setFieldValue(formatNumber(e.target.value))}
                unit={unit ? unit : ""}
                required={required}
                {...rest}
            />
        </div>
    );
}
