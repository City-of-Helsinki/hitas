import CheckboxInput from "./CheckboxInput";
import DateInput from "./DateInput";
import FileInput from "./FileInput";
import FormProviderForm from "./FormProviderForm";
import NumberInput from "./NumberInput";
import RelatedModelInput from "./RelatedModelInput";
import SaveFormButton from "./SaveFormButton";
import SelectInput from "./SelectInput";
import TextAreaInput from "./TextAreaInput";
import TextInput from "./TextInput";
import ToggleInput from "./ToggleInput";

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

export {
    CheckboxInput,
    DateInput,
    FileInput,
    FormProviderForm,
    NumberInput,
    RelatedModelInput,
    SaveFormButton,
    SelectInput,
    TextAreaInput,
    TextInput,
    ToggleInput,
};
