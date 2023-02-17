import {TextArea as HDSTextArea} from "hds-react";

import {FormInputProps} from "./";

const TextAreaInput = ({name, id = name, label = "", required, invalid, formObject, ...rest}: FormInputProps) => {
    const {
        register,
        formState: {errors},
    } = formObject;
    const formText = register(name, {required: required});
    return (
        <div className={`input-field input-field--text ${required ? "input-field--required" : ""}`}>
            <HDSTextArea
                id={id}
                name={formText.name}
                label={label}
                onChange={formText.onChange}
                onBlur={formText.onBlur}
                ref={formText.ref}
                errorText={errors[name] && errors[name].message}
                invalid={invalid ?? !!errors[name]}
                required={required}
                {...rest}
            />
        </div>
    );
};

export default TextAreaInput;
