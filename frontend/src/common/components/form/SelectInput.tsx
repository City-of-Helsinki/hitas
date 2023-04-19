import {Combobox, Select as HDSSelect} from "hds-react";

import {dotted} from "../../utils";
import {FormInputProps} from "./";

interface SelectProps extends FormInputProps {
    label: string;
    options: {
        label: string;
        value: string;
    }[];
    searchable?: boolean;
}

const Select = ({
    name,
    label,
    required,
    invalid,
    defaultValue,
    formObject,
    searchable = false,
    ...rest
}: SelectProps) => {
    formObject.register(name);
    const {
        formState: {errors},
    } = formObject;
    const fieldError = dotted(errors, name);
    const inputProps = {
        label: label,
        required: required,
        clearable: !required,
        defaultValue: defaultValue,
        ariaLabelledBy: "",
        clearButtonAriaLabel: "Tyhjennä",
        selectedItemRemoveButtonAriaLabel: "Poista",
        ...rest,
    };

    const handleChange = (newValue: {label?: string; value?: string}) => {
        if (newValue) {
            formObject.setValue(name, newValue, true);
        } else if (!required) formObject.setValue(name, null);
    };

    return (
        <div className={`input-field input-field--dropdown${required ? " input-field--required" : ""}`}>
            {searchable ? (
                <Combobox
                    {...inputProps}
                    toggleButtonAriaLabel=""
                />
            ) : (
                <>
                    <HDSSelect
                        {...inputProps}
                        label={`${label}${required ? " *" : ""}`}
                        onChange={handleChange}
                        invalid={invalid ?? !!fieldError}
                        required={true}
                    />
                    {!!fieldError && <p className="text-input_hds-text-input__error-text">{fieldError.message}</p>}
                </>
            )}
        </div>
    );
};

export default Select;
