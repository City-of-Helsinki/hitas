import React from "react";

import {TextArea, TextInput} from "hds-react";

import {CommonFormInputFieldProps} from "./FormInputField";

interface FormTextInputFieldProps extends CommonFormInputFieldProps {
    size: "small" | "large";
    placeholder?: string;
    validator?: (value) => void;
}

export default function FormTextInputField({
    value,
    setFieldValue,
    size = "small",
    required,
    validator,
    ...rest
}: FormTextInputFieldProps): React.JSX.Element {
    function handleOnChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
        setFieldValue(e.target.value);
    }

    function isValid(testValue: string) {
        if (validator !== undefined) {
            return validator(testValue);
        } else return true;
    }

    const inputProps = {
        value: value,
        onChange: handleOnChange,
        required: required,
        ...rest,
    };

    if (size === "small") {
        return (
            <div
                className={`input-field input-field--text${required ? " input-field--required" : ""} ${
                    isValid(value) ? "" : " input-field--invalid"
                }`}
            >
                <TextInput {...inputProps} />
            </div>
        );
    } else {
        return <TextArea {...inputProps} />;
    }
}
