import {format, parse} from "date-fns";
import {DateInput as HDSDateInput} from "hds-react";

import {useEffect} from "react";
import {useFormContext} from "react-hook-form";
import {dotted} from "../../utils";
import {FormInputProps} from "./";

interface DateInputProps extends FormInputProps {
    maxDate?: Date;
    minDate?: Date;
}

const DateInput = ({name, label, required, ...rest}: DateInputProps) => {
    const formObject = useFormContext();

    const hdsFormat = "d.M.yyyy";
    const apiFormat = "yyyy-MM-dd";

    const {
        register,
        watch,
        resetField,
        formState: {errors},
    } = formObject;
    const formDate = register(name, {setValueAs: (value) => (value === "" ? null : value)});
    const fieldError = dotted(errors, formDate.name);
    watch(name);

    const getValue = (): string => {
        // Try to convert Hitas API format to HDS date format
        try {
            return format(parse(formObject.getValues(formDate.name), apiFormat, new Date()), hdsFormat);
        } catch {
            return formObject.getValues(formDate.name);
        }
    };

    const handleOnChange = (newValue: string, valueAsDate: Date) => {
        // Do not format the date if the year is obviously incomplete
        if (valueAsDate.getFullYear().toString().length < 4) {
            formObject.setValue(formDate.name, newValue);
            return;
        }

        // Try to convert HDS date to Hitas API date
        try {
            const convertedValue = format(valueAsDate, apiFormat);
            formObject.setValue(formDate.name, convertedValue);
            formObject.clearErrors(name);
        } catch {
            formObject.setValue(formDate.name, newValue);
        }
    };

    // react-hook-form forces the initial value into the field without formatting.
    // This is a small hack to refresh the component to apply date formatting.
    useEffect(() => resetField(formDate.name), [resetField, formDate.name]);

    return (
        <div className={`input-field input-field--date${required ? " input-field--required" : ""}`}>
            <HDSDateInput
                id={name}
                language="fi"
                disableConfirmation
                name={formDate.name}
                label={label || ""}
                onChange={handleOnChange}
                onBlur={undefined} // formObject.onBlur will break date formatting
                ref={formDate.ref}
                value={getValue() ?? ""}
                errorText={fieldError ? (fieldError as {message: string}).message : ""}
                invalid={!!fieldError}
                required={required}
                crossOrigin={undefined}
                {...rest}
            />
        </div>
    );
};

export default DateInput;
