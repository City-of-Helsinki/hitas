import {FileInput as HDSFileInput} from "hds-react";

import {FormInputProps} from "./";

interface FileInputProps extends FormInputProps {
    buttonLabel?: string;
    accept?: string;
}
const FileInput = ({
    name,
    id = name,
    label = "",
    required,
    formObject,
    onChange,
    ...rest
}: FileInputProps): JSX.Element => {
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
                id={id}
                label={label}
                onChange={handleChange}
                errorText={errors[name] && errors[name].message}
                required={required}
                multiple={false}
                {...rest}
            />
        </div>
    );
};

export default FileInput;
