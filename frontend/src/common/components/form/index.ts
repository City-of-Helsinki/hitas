import CheckboxInput from "./CheckboxInput";
import DateInput from "./DateInput";
import FileInput from "./FileInput";
import NumberInput from "./NumberInput";
import RelatedModelInput from "./RelatedModelInput";
import SelectInput from "./SelectInput";
import TextAreaInput from "./TextAreaInput";
import TextInput from "./TextInput";
import ToggleInput from "./ToggleInput";

export type FormInputProps = {
    name: string;
    formObject?;
    label?: string;
    required?: boolean;
    invalid?: boolean;
    errorText?: string;
    key?: string;
    tooltipText?: string;
    className?: string;
    placeholder?;
    value?;
    disabled?;
    defaultValue?;
    onChange?;
    onBlur?;
};

export {
    CheckboxInput,
    DateInput,
    FileInput,
    NumberInput,
    RelatedModelInput,
    SelectInput,
    TextAreaInput,
    TextInput,
    ToggleInput,
};
