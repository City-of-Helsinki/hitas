import {ToggleButton} from "hds-react";

import {useFormContext} from "react-hook-form";
import {FormInputProps} from "./";

const ToggleInput = ({name, label, required, ...rest}: FormInputProps) => {
    const formObject = useFormContext();
    const formToggle = formObject.register(name);
    const value = formObject.getValues(formToggle.name);

    return (
        <div className={required ? "force-bold" : undefined}>
            <ToggleButton
                id={name}
                label={`${label}${required ? " *" : ""}`}
                checked={value}
                ref={formToggle.ref} // TODO is this needed?
                onChange={() => {
                    formObject.setValue(name, !value, {shouldValidate: true});
                }}
                variant="inline"
                {...rest}
            />
        </div>
    );
};

export default ToggleInput;
