import React, {useEffect, useState} from "react";

import {dotted} from "../../utils";
import FormDateInputField from "./FormDateInputField";
import FormDropdownInputField from "./FormDropdownInputField";
import FormNumberInputField from "./FormNumberInputField";
import FormOwnershipInputField from "./FormOwnershipInputField";
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
    tooltipText?: string;
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
          inputType?: "text" | "textArea" | "postalCode";
      }
    | {
          inputType?: "date";
          maxDate?: Date;
      }
    | {
          inputType: "number";
          unit?: string;
          fractionDigits?: number;
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
    | {
          inputType: "ownership";
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
                // Special case handling to allow setting the root object as null for related model fields
                if (inputType === "relatedModel" && !required) {
                    if (value) {
                        // Handle the case where a null may be in the middle of fieldPath
                        dotted(draft, fieldPath.split(".").slice(0, -1), {
                            [fieldPath.split(".").slice(-1).join(".")]: value,
                        });
                    } else {
                        // Set the entire field as null instead of only the field inside related object
                        dotted(draft, fieldPath.split(".").slice(0, -1), null);
                    }
                } else {
                    dotted(draft, fieldPath, value);
                }
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

    const value = dotted(formData, fieldPath);
    const commonProps = {
        id: `input-${fieldPath}`,
        key: `input-${fieldPath}`,
        label: label,
        value: value === undefined || value === null ? "" : value,
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

        // No options and no value in the field, show the field as invalid
        // The field may be populated even though there are no options available if the options are still loading
        // from the API, in which case it should be invalid only when no defaultValue is given
        if (
            !rest.options.length &&
            !(dotted(formData, fieldPath) || rest?.defaultValue?.value === undefined || rest.defaultValue.value === "")
        ) {
            commonProps.invalid = true;
        }

        return (
            <div className={`input-field input-field--dropdown${required ? " input-field--required" : ""}`}>
                <FormDropdownInputField
                    {...commonProps}
                    searchable={inputType === "combobox"}
                    required={required}
                    {...rest}
                />
            </div>
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
    if (inputType === "ownership") {
        if (!("getRelatedModelLabel" in rest) || rest.getRelatedModelLabel === undefined)
            throw new Error("`relatedModelLabel` is required.");
        if (!("queryFunction" in rest) || rest.queryFunction === undefined)
            throw new Error("`queryFunction` is required.");
        return (
            <FormOwnershipInputField
                {...commonProps}
                fieldPath={fieldPath}
                {...rest}
            />
        );
    }
    throw new Error("Invalid `inputType` given.");
}
