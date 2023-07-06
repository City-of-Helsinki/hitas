import {Combobox, Select} from "hds-react";

import React from "react";
import {CommonFormInputFieldProps} from "./FormInputField";

interface FormDropdownInputFieldProps extends CommonFormInputFieldProps {
    options: {
        label: string;
        value?: string;
    }[];
    defaultValue?: {
        label: string;
        value?: string;
    };
    searchable?: boolean;
}

export default function FormDropdownInputField({
    value,
    setFieldValue,
    searchable,
    required,
    ...rest
}: FormDropdownInputFieldProps): React.JSX.Element {
    const onSelectionChange = (newValue: {label: string; value?: string}) => {
        if (newValue) {
            setFieldValue(newValue?.value ? newValue?.value : newValue?.label);
        } else if (!required) {
            setFieldValue(null);
        }
    };

    const inputProps = {
        defaultValue: {label: value},
        onChange: onSelectionChange,
        clearable: !required,
        required: required,
        ...rest,
    };

    if (searchable)
        return (
            <div className={`input-field input-field--dropdown${required ? " input-field--required" : ""}`}>
                <Combobox
                    {...inputProps}
                    toggleButtonAriaLabel="Toggle menu"
                />
            </div>
        );
    else {
        return <Select {...inputProps} />;
    }
}
