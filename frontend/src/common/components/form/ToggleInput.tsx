import {ToggleButton} from "hds-react";

import {dotted} from "../../utils";
import {FormInputProps} from "./";

const ToggleInput = ({id, name, label, required, formObject}: FormInputProps) => {
    const {
        register,
        formState: {errors},
    } = formObject;
    const formToggle = register(name);
    const value = formObject.getValues(formToggle.name);
    const fieldError = dotted(errors, formToggle);

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
            {!!fieldError && <div className="error-message">{fieldError.message}</div>}
        </div>
    );
};

export default ToggleInput;
