import React, {useState} from "react";

import {Option, Select} from "hds-react";
import {useDispatch} from "react-redux";

interface FilterRelatedModelComboboxFieldProps {
    label: string;
    endpointQuery;
    labelField: string;
    filterFieldName: string;
    filterParams: object;
    setFilterParams: (object) => void;
}

export default function FilterRelatedModelComboboxField({
    label,
    endpointQuery,
    labelField,
    filterFieldName,
    filterParams,
    setFilterParams,
}: FilterRelatedModelComboboxFieldProps): React.JSX.Element {
    const dispatch = useDispatch();
    const defaultOption = filterParams && filterParams[filterFieldName] ? {label: filterParams[filterFieldName]} : null;
    const [value, setValue] = useState<Partial<Option>[]>(defaultOption ? [defaultOption] : []);

    const onSelectionChange = (selectedOptions: Option[]) => {
        const selected = selectedOptions[0];
        // Update set filter, or remove key if filter is cleared
        const filters = {...filterParams};
        if (selected) {
            filters[filterFieldName] = selected.label;
        } else {
            delete filters[filterFieldName];
        }
        setFilterParams(filters);
        setValue(selectedOptions);
    };

    return (
        <Select
            id={`filter__${filterFieldName}`}
            key={`filter__${filterFieldName}`}
            texts={{
                label,
                placeholder: "",
            }}
            options={value}
            onChange={onSelectionChange}
            onSearch={async (searchValue) => {
                const queryData = {...(searchValue ? {[labelField]: searchValue} : {})};
                const resultData = await dispatch(endpointQuery.initiate(queryData)).unwrap();
                const newOptions: Option[] = resultData.contents.map((item) => ({label: item[labelField]}));
                // NOTE: HDS Select should accept either `Option[]` or option group but as of writing only
                // option groups are accepted so the `Option[]` is wrapped in a group without a label.
                return {
                    groups: [
                        {
                            options: newOptions,
                        },
                    ],
                };
            }}
            value={value}
            clearable
        />
    );
}
