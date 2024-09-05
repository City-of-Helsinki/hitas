import {FileInput as HDSFileInput} from "hds-react";

import React, {useRef} from "react";
import {useFormContext} from "react-hook-form";
import {FormInputProps} from "./";

interface FileInputProps extends FormInputProps {
    buttonLabel?: string;
    accept?: string;
}
const FileInput = ({name, label = "", required, onChange, ...rest}: FileInputProps): React.JSX.Element => {
    const formObject = useFormContext();
    const containerRef = useRef(null);

    const {
        register,
        formState: {errors},
    } = formObject;
    register(name, {required: required});

    const handleChange = (filesArray) => {
        // File is a required field but the HDS file input clears the native input after selection so the form is always invalid.
        // This is a hack to make sure the native input has a file if the user has selected one so that the form can be submitted.
        const containerElement = containerRef.current as HTMLElement | null;
        const fileInput = containerElement?.querySelector('input[type="file"]') as HTMLInputElement | null;
        if (fileInput) {
            const datatransfer = new DataTransfer();
            datatransfer.items.add(filesArray[0]);
            setTimeout(() => (fileInput.files = datatransfer.files), 10);
        }
        // Explicitly mark as dirty, since react-hook-form does not support File objects for dirty checking.
        formObject.setValue(name, filesArray[0], {shouldDirty: true});
        // If there is an onChange handler, call it
        onChange && onChange(filesArray);
    };

    return (
        <div
            ref={containerRef}
            className="input-field--file"
        >
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
