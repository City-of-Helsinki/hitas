import Checkbox from "./Checkbox";
import DateInput from "./DateInput";
import NumberInput from "./NumberInput";
import RelatedModelInput from "./RelatedModelInput";
import Select from "./SelectInput";
import TextAreaInput from "./TextAreaInput";
import TextInput from "./TextInput";
import ToggleInput from "./ToggleInput";

export type FormInputProps = {
    name: string;
    id?: string;
    formObject?;
    label?: string;
    required?: boolean;
    invalid?: boolean;
    errorText?: string;
    key?: string;
    tooltipText?: string;
    placeholder?;
    value?;
    disabled?;
    defaultValue?;
    onChange?;
    onBlur?;
};

export {TextInput, TextAreaInput, NumberInput, DateInput, Select, Checkbox, ToggleInput, RelatedModelInput};
