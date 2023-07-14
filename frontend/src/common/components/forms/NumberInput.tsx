import {NumberInput as HDSNumberInput} from "hds-react";

import {useFormContext} from "react-hook-form";
import {dotted} from "../../utils";
import {FormInputProps} from "./";

interface FormNumberInputProps extends FormInputProps {
    unit?: string;
    field?: object;
    allowDecimals?: boolean;
}

const NumberInput = ({name, label = "", unit, required, invalid, allowDecimals, ...rest}: FormNumberInputProps) => {
    const formObject = useFormContext();

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

    // React Hook Form doesn't like us manually setting the value of the input field,
    // this is a bit hacky way of doing this, but it works in most cases.
    // These characters are valid in the NumberField, but we don't want to allow them to be entered
    const bannedCharacters = ["ArrowUp", "ArrowDown", "e", "E", "+", "-"];
    if (!allowDecimals) bannedCharacters.push(".", ",");
    const handleKeyDown = (e) => {
        if (bannedCharacters.includes(e.key)) {
            e.preventDefault();
        }
    };

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
                onKeyDown={handleKeyDown}
                errorText={fieldError ? (fieldError as {message: string}).message : ""}
                invalid={invalid ?? !!fieldError}
                required={required}
                {...rest}
            />
        </div>
    );
};

export default NumberInput;
