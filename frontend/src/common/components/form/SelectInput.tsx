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
    setDirectValue?: boolean;
}

const Select = ({
    name,
    label,
    required,
    invalid,
    defaultValue,
    formObject,
    searchable = false,
    setDirectValue = false, // If true, set the `value` of the option, otherwise sets the whole option object
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
            if (setDirectValue) {
                formObject.setValue(name, newValue.value);
            } else {
                formObject.setValue(name, newValue);
            }
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
                        label={label}
                        onChange={handleChange}
                        invalid={invalid ?? !!errors[name]}
                        required={required}
                        clearable={!required}
                    />
                    {!!fieldError && <p className="text-input_hds-text-input__error-text">{fieldError.message}</p>}
                </>
            )}
        </div>
    );
};

export default Select;
