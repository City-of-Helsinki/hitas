export {default as CheckboxInput} from "./CheckboxInput";
export {default as DateInput} from "./DateInput";
export {default as FileInput} from "./FileInput";
export {default as FormProviderForm} from "./FormProviderForm";
export {default as NumberInput} from "./NumberInput";
export {default as RelatedModelInput} from "./RelatedModelInput";
export {default as SaveFormButton} from "./SaveFormButton";
export {default as SelectInput} from "./SelectInput";
export {default as TextAreaInput} from "./TextAreaInput";
export {default as TextInput} from "./TextInput";
export {default as ToggleInput} from "./ToggleInput";

export type FormInputProps = {
    name: string;
    label?: string;
    required?: boolean;
    invalid?: boolean;
    errorText?: string;
    key?: string;
    tooltipText?: string;
    className?: string;
    value?;
    disabled?;
    defaultValue?;
    onChange?;
    onBlur?;
};
