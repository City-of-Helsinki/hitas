import {NumberInput as HDSNumberInput} from "hds-react";

import {dotted} from "../../utils";
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
        watch,
        formState: {errors},
    } = formObject;
    const formNumber = register(name, {valueAsNumber: true});
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

    const fieldError = dotted(errors, formNumber.name);
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
                errorText={!!fieldError && fieldError.message}
                invalid={invalid ?? !!fieldError}
                required={required}
                {...rest}
            />
        </div>
    );
};

export default NumberInput;
