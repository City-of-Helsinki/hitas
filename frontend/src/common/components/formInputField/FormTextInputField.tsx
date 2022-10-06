import React from "react";

import {TextArea, TextInput} from "hds-react";

import {CommonFormInputFieldProps} from "./FormInputField";

interface FormTextInputFieldProps extends CommonFormInputFieldProps {
    size: "small" | "large";
    placeholder?: string;
}

export default function FormTextInputField({
    setFieldValue,
    size = "small",
    required,
    ...rest
}: FormTextInputFieldProps): JSX.Element {
    function handleOnChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
        setFieldValue(e.target.value);
    }

    const inputProps = {
        onChange: handleOnChange,
        required: required,
        ...rest,
    };

    if (size === "small") {
        return (
            <div className={`input-field input-field--text${required ? " input-field--required" : ""}`}>
                <TextInput {...inputProps} />
            </div>
        );
    } else {
        return <TextArea {...inputProps} />;
    }
}
