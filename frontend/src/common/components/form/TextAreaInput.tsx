import {TextArea as HDSTextArea} from "hds-react";

import {dotted} from "../../utils";
import {FormInputProps} from "./";

const TextAreaInput = ({name, id = name, label = "", required, invalid, formObject, ...rest}: FormInputProps) => {
    const {
        register,
        formState: {errors},
    } = formObject;
    const formText = register(name, {required: required});
    const fieldError = dotted(errors, formText.name);

    return (
        <div className={`input-field input-field--text ${required ? "input-field--required" : ""}`}>
            <HDSTextArea
                id={id}
                name={formText.name}
                label={label}
                onChange={formText.onChange}
                onBlur={formText.onBlur}
                ref={formText.ref}
                errorText={!!fieldError && fieldError.message}
                invalid={invalid ?? !!fieldError}
                required={required}
                {...rest}
            />
        </div>
    );
};

export default TextAreaInput;
