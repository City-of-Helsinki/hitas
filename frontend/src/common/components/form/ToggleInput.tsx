import {ToggleButton} from "hds-react";

import {FormInputProps} from "./";

const ToggleInput = ({id, name, label, required, formObject}: FormInputProps) => {
    const {
        register,
        formState: {errors},
    } = formObject;
    const formToggle = register(name);
    const value = formObject.getValues(formToggle.name);
    return (
        <div className={required ? "force-bold" : ""}>
            <ToggleButton
                id={id || name}
                label={`${label}${required ? " *" : ""}`}
                checked={value}
                ref={formToggle.ref}
                onChange={() => {
                    formObject.setValue(formToggle.name, !value, {shouldValidate: true});
                }}
                variant="inline"
            />
            {errors[formToggle.name] && <div className="error-message">{errors[formToggle.name].message}</div>}
        </div>
    );
};

export default ToggleInput;
