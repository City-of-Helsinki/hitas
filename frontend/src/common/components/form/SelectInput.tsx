import {Combobox, Select as HDSSelect} from "hds-react";

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
                    <legend style={{fontWeight: required ? "bold" : "normal"}}>{label + (required ? " *" : "")}</legend>
                    <HDSSelect
                        {...inputProps}
                        label=""
                        onChange={handleChange}
                        invalid={invalid ?? !!errors[name]}
                        required={required}
                    />
                    {errors[name] && <p className="text-input_hds-text-input__error-text">{errors[name].message}</p>}
                </>
            )}
        </div>
    );
};

export default Select;
