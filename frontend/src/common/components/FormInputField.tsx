import React, {useState} from "react";

import {format, parse} from "date-fns";
import {Combobox, DateInput, NumberInput, Select, TextArea, TextInput} from "hds-react";

import {dotted} from "../utils";

interface IFormInputField {
    inputType?: "text" | "textArea" | "postalCode" | "money" | "select" | "combobox" | "date";
    label: string;
    fieldPath: string | string[];
    options?: {label: string}[];
    required?: boolean;
    validator?: (value) => boolean;
    formData: object;
    setFormData: (draft) => void;
}

export default function FormInputField({
    inputType = "text",
    label,
    fieldPath,
    options,
    required,
    validator,
    formData,
    setFormData,
}: IFormInputField) {
    const [isInvalid, setIsInvalid] = useState(false);

    const setFieldValue = (value) => {
        if (validator !== undefined) setIsInvalid(!validator(value));
        else if (required) setIsInvalid(!value);

        setFormData((draft) => {
            dotted(draft, fieldPath, value);
        });
    };

    const inputProps = {
        label: label,
        id: `input-${fieldPath}`,
        key: `input-${fieldPath}`,
        required: required || false,
        invalid: isInvalid,
    };

    if (inputType === "text") {
        return (
            <TextInput
                {...inputProps}
                value={dotted(formData, fieldPath) || ""}
                onChange={(e) => setFieldValue(e.target.value)}
            />
        );
    } else if (inputType === "textArea") {
        return (
            <TextArea
                {...inputProps}
                value={dotted(formData, fieldPath) || ""}
                onChange={(e) => setFieldValue(e.target.value)}
            />
        );
    } else if (inputType === "postalCode") {
        const currentValue = dotted(formData, fieldPath) || "";

        const handleOnChange = (e: React.ChangeEvent<HTMLInputElement>) => {
            // Remove all non-number characters from the value
            const value = e.target.value.replace(/\D/g, "");
            setFieldValue(value);
        };

        const handleOnBlur = (e: React.ChangeEvent<HTMLInputElement>) => {
            if ((required && e.target.value.length !== 5) || (!required && !e.target.value.length)) {
                setIsInvalid(true);
            }
        };

        return (
            <TextInput
                {...inputProps}
                value={currentValue}
                onChange={handleOnChange}
                onBlur={handleOnBlur}
                onFocus={() => setIsInvalid(false)}
                maxLength={5}
            />
        );
    } else if (inputType === "money") {
        return (
            <NumberInput
                {...inputProps}
                value={dotted(formData, fieldPath) || ""}
                onChange={(e) => setFieldValue(Number(Number(e.target.value).toFixed(2)))}
                unit="€"
            />
        );
    } else if (inputType === "combobox" || inputType === "select") {
        if (options === undefined || !options.length)
            throw new Error("`options` argument is required when `inputType` is `select` or `combobox`.");

        const onSelectionChange = (value: {label: string}) => {
            if (value) {
                setFieldValue(value.label);
            } else if (!required) {
                setFieldValue(null);
            }
        };

        if (inputType === "select")
            return (
                <Select
                    {...inputProps}
                    defaultValue={{label: dotted(formData, fieldPath)}}
                    onChange={onSelectionChange}
                    options={options}
                    clearable={!required}
                />
            );
        return (
            <Combobox
                {...inputProps}
                defaultValue={{label: dotted(formData, fieldPath)}}
                onChange={onSelectionChange}
                options={options}
                clearable={!required}
                toggleButtonAriaLabel="Toggle menu"
            />
        );
    } else if (inputType === "date") {
        // Display the date in 'HDS date format' to the user, but internally keep the date stored in a format which
        // doesn't need to be converted before sending it to the API

        const hdsFormat = "dd.MM.yyyy";
        const apiFormat = "yyyy-MM-dd";

        const apiDateFormatToHdsDateFormat = (value: string) => format(parse(value, apiFormat, new Date()), hdsFormat);
        const dateToHitasDateFormat = (value: Date) => format(value, apiFormat);

        return (
            <DateInput
                {...inputProps}
                value={(() => {
                    const value = dotted(formData, fieldPath) || "";
                    try {
                        return apiDateFormatToHdsDateFormat(value);
                    } catch {
                        return value;
                    }
                })()}
                onChange={(newValue: string, valueAsDate: Date) => {
                    // Do not format the date if the year is obviously incomplete
                    if (valueAsDate.getFullYear().toString().length < 4) {
                        setFieldValue(newValue);
                        setIsInvalid(true);
                        return;
                    }
                    try {
                        const convertedValue = dateToHitasDateFormat(valueAsDate);
                        setFieldValue(convertedValue);
                        setIsInvalid(false);
                    } catch {
                        setFieldValue(newValue);
                        setIsInvalid(true);
                    }
                }}
                language={"fi"}
                disableConfirmation={true}
            />
        );
    }
    throw new Error("Invalid `inputType` given.");
}
