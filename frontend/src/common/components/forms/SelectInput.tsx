import {Option, Select as HDSSelect} from "hds-react";

import {useFormContext} from "react-hook-form";
import {dotted} from "../../utils";
import {FormInputProps} from "./";
import {useCallback, useState} from "react";

interface SelectProps extends FormInputProps {
    label: string;
    options: {
        label: string;
        value: string;
    }[];
    defaultValue?: string;
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
        defaultValue = dotted(formState.defaultValues as object, name) as string | undefined;
    }
    // Find the option with value corresponding to defaultValue from the options
    const defaultOption = options.find((option) => option.value === defaultValue);

    if (defaultValue && !defaultOption) {
        // eslint-disable-next-line no-console
        console.warn(`SelectInput: No default option found for value ${defaultValue}!`);
    }

    const [value, setValue] = useState<Partial<Option>[]>(defaultOption ? [defaultOption] : []);

    const inputProps = {
        required: required,
        clearable: !required,
        options: options,
        value: value,
        onChange: () => {},
        texts: {
            label,
        },
        ...rest,
    };

    const handleChange = useCallback((selected: Option[]) => {
        if (selected.length === 1) {
            if (setDirectValue) {
                formObject.setValue(name, selected[0].value);
            } else {
                formObject.setValue(name, selected[0]);
            }
        } else if (selected.length > 1) {
            throw new Error("Not implemented: Multiple selections in SelectInput");
        } else if (!required) {
            formObject.setValue(name, null);
        }
        setValue(selected);
    }, []);

    return (
        <div className={`input-field input-field--dropdown${required ? " input-field--required" : ""}`}>
            {searchable ? (
                <HDSSelect {...inputProps} />
            ) : (
                <>
                    <HDSSelect
                        {...inputProps}
                        texts={{
                            ...inputProps.texts,
                            error: fieldError ? (fieldError as {message: string}).message : "",
                        }}
                        onChange={handleChange}
                        invalid={invalid ?? !!errors[name]}
                    />
                </>
            )}
        </div>
    );
};

export default SelectInput;
