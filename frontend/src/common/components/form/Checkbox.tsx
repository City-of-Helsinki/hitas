import {Checkbox as HDSCheckbox} from "hds-react";

import {FormInputProps} from "./";

const Checkbox = ({
    name,
    id = name,
    label,
    required,
    formObject,
    triggerField,
    ...rest
}: FormInputProps & {triggerField?: string}) => {
    const {register} = formObject;
    const formCheckbox = register(name);

    const handleChange = () => {
        formObject.setValue(formCheckbox.name, !formObject.getValues(formCheckbox.name), {shouldValidate: true});
        if (triggerField) {
            formObject.trigger(triggerField);
        }
    };

    return (
        <HDSCheckbox
            id={id}
            name={name}
            label={`${label}${required ? " *" : ""}`}
            checked={formObject.getValues(formCheckbox.name)}
            onChange={handleChange}
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
