import {TextInput as HDSTextInput} from "hds-react";

import {FormInputProps} from "./";

const TextInput = ({name, id = name, label = "", required, invalid, formObject, ...rest}: FormInputProps) => {
    const {
        register,
        formState: {errors},
    } = formObject;
    const formText = register(name, {required: required});
    return (
        <div className={`input-field input-field--text ${required ? "input-field--required" : ""}`}>
            <HDSTextInput
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

export default TextInput;
