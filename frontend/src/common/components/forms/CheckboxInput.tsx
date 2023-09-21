import {Checkbox as HDSCheckbox} from "hds-react";

import {useFormContext} from "react-hook-form";
import {FormInputProps} from "./";

const CheckboxInput = ({
    name,
    label,
    required,
    triggerField, // Used to trigger validation of another field, in case validation is related to this checkbox
    tooltipText,
    ...rest
}: FormInputProps & {triggerField?: string} & {
    tooltipText?: string;
}) => {
    const formObject = useFormContext();
    const {register} = formObject;
    const formCheckbox = register(name);

    const handleChange = (e) => {
        formCheckbox.onChange(e);
        if (triggerField) {
            formObject.trigger(triggerField);
        }
    };

    return (
        <HDSCheckbox
            id={name}
            name={name}
            label={`${label}${required ? " *" : ""}`}
            checked={formObject.getValues(formCheckbox.name)}
            onChange={handleChange}
            onBlur={formCheckbox.onBlur}
            ref={formCheckbox.ref}
            style={{
                fontWeight: required ? "700" : "500",
            }}
            tooltipText={tooltipText}
            {...rest}
        />
    );
};

export default CheckboxInput;
