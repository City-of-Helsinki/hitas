import React, {useEffect, useState} from "react";

import {Combobox} from "hds-react";

interface FilterRelatedModelComboboxFieldProps {
    label: string;
    queryFunction;
    labelField: string;
    filterFieldName: string;
    filterParams: object;
    setFilterParams: (object) => void;
}

export default function FilterRelatedModelComboboxField({
    label,
    queryFunction,
    labelField,
    filterFieldName,
    filterParams,
    setFilterParams,
}: FilterRelatedModelComboboxFieldProps): React.JSX.Element {
    const MIN_LENGTH = 2; // Minimum characters before querying more data from the API
    const [queryFilterValue, setQueryFilterValue] = useState("");
    const [options, setOptions] = useState([{label: "Loading...", disabled: true}]);
    const [isQuerySkipped, setIsQuerySkipped] = useState(true);

    const {data} = queryFunction(
        {...(queryFilterValue ? {[labelField]: queryFilterValue} : {})},
        {skip: isQuerySkipped}
    );

    useEffect(() => {
        if (data && data.contents) {
            const tempOptions = data.contents.map((o) => {
                return {label: o[labelField]};
            });
            // Not all data can be loaded to the dropdown, indicate that there's more results available
            if (data.page.total_pages > 1) {
                tempOptions.push({label: "Lataa lisää tuloksia hakemalla", disabled: true});
            } else if (data.contents.length === 0) {
                tempOptions.push({label: "Ei tuloksia", disabled: true});
            }
            setOptions(tempOptions);
        }
    }, [data, labelField]);

    const onSelectionChange = (value: {label: string}) => {
        // Update set filter, or remove key if filter is cleared
        const filters = {...filterParams};
        if (!value) {
            delete filters[filterFieldName];
            setFilterParams(filters);
            return;
        }
        filters[filterFieldName] = value.label;
        setFilterParams(filters);
    };

    const filterFunction = (options, search: string) => {
        // Method is overwritten only to access raw text input,
        // which allows fetching more results from the API when typing

        // No need to set the state on every render, if the value hasn't changed
        if (search !== queryFilterValue) {
            // As we don't have access to the search value state of the combobox, setting setQueryFilterValue state
            // here will raise an error:
            //  Warning: Cannot update a component (`RelatedModelFilterCombobox`) while rendering a different component (`T`). To locate the bad setState() call inside `T`, follow the stack trace as described in https://reactjs.org/link/setstate-in-render
            // Having the possibility to handle the search value's state outside the Combobox would fix this
            // issue, but a fix is not possible at this time (unless the HDS Combobox is reimplemented with that fix)
            // Instead, let's just disable warnings temporarily, as no bad effects caused by this has been noticed
            /* eslint-disable no-console */
            const backup = console.error;
            console.error = () => null;
            if (queryFilterValue && (!search || search.length < MIN_LENGTH)) {
                setQueryFilterValue("");
            } else if (search.length >= 2) {
                setQueryFilterValue(search);
            }
            console.error = backup;
        }

        // If there's no results (Only one option, which is disabled), display it
        if (options.length === 1 && options[0].disabled) {
            return options;
        }

        // Original filtering functionality
        return options.filter((option) => {
            return option["label"].toLowerCase().indexOf(search.toLowerCase()) > -1;
        });
    };

    return (
        <Combobox
            id={`filter__${filterFieldName}`}
            key={`filter__${filterFieldName}`}
            label={label}
            options={options}
            isOptionDisabled={(option) => option?.disabled}
            toggleButtonAriaLabel="Toggle menu"
            onChange={onSelectionChange}
            onFocus={() => setIsQuerySkipped(false)} // Load options only after field is focused to reduce unnecessary api queries
            onBlur={() => setIsQuerySkipped(true)}
            filter={filterFunction}
            clearable
        />
    );
}
