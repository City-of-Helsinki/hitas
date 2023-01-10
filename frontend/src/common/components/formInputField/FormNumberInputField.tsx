import React from "react";

import {NumberInput} from "hds-react";

import {CommonFormInputFieldProps} from "./FormInputField";

interface FormNumberInputFieldProps extends Omit<CommonFormInputFieldProps, "value"> {
    value: number;
    fractionDigits?: number;
    unit?: string;
}

export default function FormNumberInputField({
    value,
    setFieldValue,
    unit,
    fractionDigits = 0,
    required,
    ...rest
}: FormNumberInputFieldProps): JSX.Element {
    // Format the passed value depending on fractionDigits without rounding or stripping trailing zeroes
    const re = new RegExp(fractionDigits > 0 ? `(\\d+\\.\\d{${fractionDigits}})(\\d)` : "(\\d+)");
    const toFixedDown = (v: string): string => {
        if (v[0] === ".") v = "0" + v; // Prepend a zero if string starts with a dot
        const m = v.toString().match(re);
        return m ? m[1] : v;
    };

    // These characters are valid in the NumberField, but we don't want to allow them to be entered
    const bannedCharacters = ["e", "E", "+", "-"];
    if (fractionDigits === 0) bannedCharacters.push(".");

    const handleWheel = (e) => {
        e.target.blur();
        e.stopPropagation();
        setTimeout(() => {
            e.target.focus();
        }, 0);
    };

    return (
        <div className={`input-field input-field--number${required ? " input-field--required" : "foo"}`}>
            <NumberInput
                value={value}
                onChange={(e) => setFieldValue(toFixedDown(e.target.value))}
                onKeyDown={(e) => bannedCharacters.includes(e.key) && e.preventDefault()}
                onWheel={(e) => handleWheel(e)}
                unit={unit || ""}
                required={required}
                {...rest}
            />
        </div>
    );
}
