import {TextInput as HDSTextInput} from "hds-react";

import {useFormContext} from "react-hook-form";
import {dotted} from "../../utils";
import {FormInputProps} from "./";

const TextInput = ({name, label = "", required, invalid, ...rest}: FormInputProps) => {
    const formObject = useFormContext();

    const {
        register,
        formState: {errors},
    } = formObject;
    const formText = register(name, {required: required});
    const fieldError = dotted(errors, formText.name);

    return (
        <div className={`input-field input-field--text ${required ? "input-field--required" : ""}`}>
            <HDSTextInput
                id={name}
                name={formText.name}
                label={label}
                onChange={formText.onChange}
                onBlur={formText.onBlur}
                ref={formText.ref}
                errorText={fieldError ? (fieldError as {message: string}).message : ""}
                invalid={invalid ?? !!fieldError}
                required={required}
                {...rest}
            />
        </div>
    );
};

export default TextInput;
