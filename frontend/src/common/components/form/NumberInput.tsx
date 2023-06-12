import {NumberInput as HDSNumberInput} from "hds-react";

import {dotted} from "../../utils";
import {FormInputProps} from "./";

interface FormNumberInputProps extends FormInputProps {
    unit?: string;
    field?: object;
    fractionDigits?: number;
}

const NumberInput = ({
    name,
    label = "",
    unit,
    required,
    invalid,
    formObject,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    fractionDigits = 0, // TODO: Add support for this
    ...rest
}: FormNumberInputProps) => {
    const {
        register,
        watch,
        formState: {errors},
    } = formObject;
    const formNumber = register(name, {
        setValueAs: (value) => (!value && value !== 0 ? null : Number(value)),
    });
    const fieldError = dotted(errors, formNumber.name);
    watch(name);

    const handleWheel = (e) => {
        if (document.activeElement === e.target) {
            e.target.blur();
            e.stopPropagation();
            setTimeout(() => {
                e.target.focus();
            }, 0);
        }
    };

    return (
        <div className={`input-field input-field--number${required ? " input-field--required" : ""}`}>
            <HDSNumberInput
                id={name}
                label={label ?? ""}
                ref={formNumber.ref}
                type="number"
                unit={unit}
                name={formNumber.name}
                onChange={formNumber.onChange}
                onBlur={formNumber.onBlur}
                onWheel={handleWheel}
                errorText={fieldError ? (fieldError as {message: string}).message : ""}
                invalid={invalid ?? !!fieldError}
                required={required}
                {...rest}
            />
        </div>
    );
};

export default NumberInput;
