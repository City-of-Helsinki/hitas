import React, {useState} from "react";

import {Checkbox} from "hds-react";

interface FilterCheckboxFieldProps {
    label: string;
    filterFieldName: string;
    filterParams: object;
    setFilterParams: (object) => void;
    applyOnlyOnTrue: boolean;
}

export default function FilterCheckboxField({
    label,
    filterFieldName,
    filterParams,
    setFilterParams,
    applyOnlyOnTrue = false,
}: FilterCheckboxFieldProps): React.JSX.Element {
    const [isInputChecked, setIsInputChecked] = useState(false);

    const handleOnChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const isChecked = e.target.checked;
        setIsInputChecked(isChecked);

        const filters = {...filterParams};
        if (applyOnlyOnTrue) {
            if (!isChecked) {
                delete filters[filterFieldName];
                setFilterParams(filters);
                return;
            }
        }
        filters[filterFieldName] = isChecked;
        setFilterParams(filters);
    };

    return (
        <Checkbox
            id={`filter__${filterFieldName}`}
            label={label}
            checked={isInputChecked}
            onChange={handleOnChange}
        />
    );
}
