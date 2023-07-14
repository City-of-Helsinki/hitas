import {Combobox, Select as HDSSelect} from "hds-react";

import {useFormContext} from "react-hook-form";
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

const SelectInput = ({
    name,
    label,
    required,
    invalid,
    options,
    defaultValue,
    searchable = false,
    setDirectValue = false, // If true, set the `value` of the option, otherwise sets the whole option object
    ...rest
}: SelectProps) => {
    const formObject = useFormContext();

    formObject.register(name);

    const {
        formState,
        formState: {errors},
    } = formObject;

    const fieldError = dotted(errors, name);

    // If form has an initial value defined for this field, use it
    if (!defaultValue && formState.defaultValues) {
        defaultValue = dotted(formState.defaultValues as object, name);
    }
    // Find the defaultValue option from the options
    defaultValue = options.find((option) => option.value === defaultValue);

    const inputProps = {
        label: label,
        required: required,
        clearable: !required,
        options: options,
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
                    />
                    {!!fieldError && (
                        <p className="text-input_hds-text-input__error-text">
                            {(fieldError as {message: string}).message}
                        </p>
                    )}
                </>
            )}
        </div>
    );
};

export default SelectInput;
