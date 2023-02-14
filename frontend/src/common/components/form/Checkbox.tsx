import {Checkbox as HDSCheckbox} from "hds-react";

import {FormInputProps} from "./";

const Checkbox = ({name, id = name, label, required, formObject, ...rest}: FormInputProps) => {
    const formCheckbox = formObject.register(name);
    const handleChange = (e) => {
        formObject.setValue(formCheckbox.name, !formObject.getValues(formCheckbox.name), {shouldValidate: true});
    };
    return (
        <HDSCheckbox
            id={id}
            name={name}
            label={`${label}${required ? " *" : ""}`}
            checked={formObject.getValues(formCheckbox.name)}
            onChange={(e) => handleChange(e)}
            onBlur={formCheckbox.onBlur}
            ref={formCheckbox.ref}
            style={{
                fontWeight: required ? "700" : "500",
            }}
            {...rest}
        />
    );
};

export default Checkbox;
