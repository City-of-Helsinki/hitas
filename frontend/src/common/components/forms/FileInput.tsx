import {FileInput as HDSFileInput} from "hds-react";

import React from "react";
import {useFormContext} from "react-hook-form";
import {FormInputProps} from "./";

interface FileInputProps extends FormInputProps {
    buttonLabel?: string;
    accept?: string;
}
const FileInput = ({name, label = "", required, onChange, ...rest}: FileInputProps): React.JSX.Element => {
    const formObject = useFormContext();

    const {
        register,
        formState: {errors},
    } = formObject;
    register(name, {required: required});

    const handleChange = (e) => {
        // Set the value of the input to the file selected
        formObject.setValue(name, e[0]);
        // If there is an onChange handler, call it
        onChange && onChange(e);
    };

    return (
        <div className="input-field--file">
            <HDSFileInput
                id={name}
                label={label}
                onChange={handleChange}
                errorText={errors[name] && (errors[name] as unknown as {message: string}).message} // FIXME
                required={required}
                multiple={false}
                {...rest}
            />
        </div>
    );
};

export default FileInput;
