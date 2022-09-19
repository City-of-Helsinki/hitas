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
    placeholder,
    ...rest
}: FormTextInputFieldProps): JSX.Element {
    function handleOnChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
        setFieldValue(e.target.value);
    }

    const inputProps = {
        onChange: handleOnChange,
        placeholder,
        ...rest,
    };

    if (size === "small") {
        return <TextInput {...inputProps} />;
    } else {
        return <TextArea {...inputProps} />;
    }
}
