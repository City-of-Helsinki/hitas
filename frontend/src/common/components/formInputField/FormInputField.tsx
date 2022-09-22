import React, {useEffect, useState} from "react";

import {dotted} from "../../utils";
import FormDateInputField from "./FormDateInputField";
import FormDropdownInputField from "./FormDropdownInputField";
import FormNumberInputField from "./FormNumberInputField";
import FormPostalCodeInputField from "./FormPostalCodeInputField";
import FormRelatedModelInputField from "./FormRelatedModelInputField";
import FormTextInputField from "./FormTextInputField";

export interface CommonFormInputFieldProps {
    id: string;
    key: string;
    label: string;
    value: string;
    required?: boolean;
    setFieldValue: (value) => void;
}

type FormInputFieldProps = {
    label: string;
    fieldPath: string;
    unit?: string;
    validator?: (value) => boolean;
    required?: boolean;
    tooltipText?: string;
    formData: object;
    setFormData?: (draft) => void;
    setterFunction?;
    error;
    placeholder?: string;
    className?: string;
} & (
    | {
          inputType?: "text" | "textArea" | "postalCode" | "number" | "date";
      }
    | {
          inputType: "select" | "combobox";
          options: {
              label: string;
              value?: string;
          }[];
          defaultValue?: {
              label: string;
              value?: string;
          };
      }
    | {
          inputType: "relatedModel";
          queryFunction;
          requestedField?: string;
          relatedModelSearchField: string;
          getRelatedModelLabel: (unknown) => string;
      }
);

export default function FormInputField({
    inputType = "text",
    label,
    fieldPath,
    unit,
    required,
    validator,
    formData,
    setFormData,
    setterFunction, // Alternate value setter which allows managing the data outside this form field
    error,
    className,
    ...rest
}: FormInputFieldProps): JSX.Element {
    const [isInvalid, setIsInvalid] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");

    const setFieldValue = (value) => {
        if (validator !== undefined) setIsInvalid(!validator(value));
        else if (required) setIsInvalid(!value);

        if (setterFunction === undefined) {
            if (setFormData === undefined) throw new Error("setFormData MISSING");

            setFormData((draft) => {
                dotted(draft, fieldPath, value);
            });
        } else {
            setterFunction(value);
        }
    };

    useEffect(() => {
        const errorFields = error?.data?.fields;
        if (errorFields !== undefined) {
            setErrorMessage(errorFields[errorFields.findIndex((e) => e.field === fieldPath)]?.message || "");
            if (errorMessage) {
                setIsInvalid(true);
            }
        }
    }, [error, errorMessage, setErrorMessage, fieldPath]);

    const commonProps = {
        id: `input-${fieldPath}`,
        key: `input-${fieldPath}`,
        label: label,
        value: dotted(formData, fieldPath) || "",
        required: required,
        invalid: isInvalid,
        setFieldValue: setFieldValue,
        errorText: errorMessage,
        className: `input-field input-field--${inputType} ${className ? className : ""}`,
    };

    if (inputType === "text" || inputType === "textArea") {
        return (
            <FormTextInputField
                {...commonProps}
                size={inputType === "text" ? "small" : "large"}
                {...rest}
            />
        );
    }
    if (inputType === "number") {
        return (
            <FormNumberInputField
                {...commonProps}
                unit={unit}
                {...rest}
            />
        );
    }
    if (inputType === "postalCode") {
        return (
            <FormPostalCodeInputField
                {...commonProps}
                setIsInvalid={setIsInvalid}
                {...rest}
            />
        );
    }
    if (inputType === "combobox" || inputType === "select") {
        if (!("options" in rest) || rest.options === undefined)
            throw new Error("`options` argument is required when `inputType` is `select` or `combobox`.");

        if (!rest.options.length) {
            commonProps.invalid = true;
        }

        return (
            <FormDropdownInputField
                {...commonProps}
                searchable={inputType === "combobox"}
                {...rest}
            />
        );
    }
    if (inputType === "date") {
        return (
            <FormDateInputField
                {...commonProps}
                setIsInvalid={setIsInvalid}
                {...rest}
            />
        );
    }
    if (inputType === "relatedModel") {
        if (!("getRelatedModelLabel" in rest) || rest.getRelatedModelLabel === undefined)
            throw new Error("`relatedModelLabel` is required.");
        if (!("queryFunction" in rest) || rest.queryFunction === undefined)
            throw new Error("`queryFunction` is required.");

        return (
            <FormRelatedModelInputField
                {...commonProps}
                fieldPath={fieldPath}
                {...rest}
            />
        );
    }
    throw new Error("Invalid `inputType` given.");
}
