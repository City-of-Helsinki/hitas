import {ToggleButton} from "hds-react";

import {FormInputProps} from "./";

const ToggleInput = ({id, name, label, required, formObject, ...rest}: FormInputProps) => {
    const {register} = formObject;
    const formToggle = register(name);
    const value = formObject.getValues(formToggle.name);

    return (
        <div className={required ? "force-bold" : undefined}>
            <ToggleButton
                id={id || name}
                label={`${label}${required ? " *" : ""}`}
                checked={value}
                ref={formToggle.ref}
                onChange={() => {
                    formObject.setValue(formToggle.name, !value, {shouldValidate: true});
                }}
                variant="inline"
                {...rest}
            />
        </div>
    );
};

export default ToggleInput;
