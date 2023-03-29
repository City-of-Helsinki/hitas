import {NumberInput as HDSNumberInput} from "hds-react";

import {FormInputProps} from "./";

interface FormNumberInputProps extends FormInputProps {
    unit?: string;
    fractionDigits?: number;
    field?: object;
}

const NumberInput = ({
    name,
    label = "",
    unit,
    fractionDigits = 0,
    required,
    invalid,
    formObject,
    ...rest
}: FormNumberInputProps) => {
    const {
        register,
        formState: {errors},
    } = formObject;
    const formNumber = register(name, {valueAsNumber: true});

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
                type="number"
                label={label ?? ""}
                id={name}
                name={formNumber.name}
                unit={unit}
                onChange={formNumber.onChange}
                onBlur={formNumber.onBlur}
                ref={formNumber.ref}
                onWheel={handleWheel}
                errorText={!!errors[formNumber.name] && errors[formNumber.name].message}
                invalid={invalid ?? !!errors[formNumber.name]}
                required={required}
                {...rest}
            />
        </div>
    );
};

export default NumberInput;
