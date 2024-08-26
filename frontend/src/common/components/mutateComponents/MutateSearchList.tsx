import {Button, IconCrossCircle, IconPlus, IconSearch, TextInput} from "hds-react";
import {useCallback, useRef, useState} from "react";
import {QueryStateHandler} from "../index";
import {IMutateFormProps, MutateModal} from "./index";

interface IResultListProps<
    TFilterQueryParams extends object,
    TListFieldsWithTitles extends object,
    TFormFieldsWithTitles extends object,
> {
    listFieldsWithTitles: TListFieldsWithTitles;
    params: TFilterQueryParams;
    searchStringMinLength: number;
    resultListMaxRows: number;
    useGetQuery;
    MutateFormComponent;
    dialogTitles?: {modify?: string; new?: string};
    setEmptyFilterParams?: () => void;
    mutateFormProps?: IMutateFormProps<TFormFieldsWithTitles>;
}

function ResultList<
    TFilterQueryParams extends object,
    TDefaultObject extends object,
    TListFieldsWithTitles extends object,
    TFormFieldsWithTitles extends object,
>({
    listFieldsWithTitles,
    params,
    searchStringMinLength,
    resultListMaxRows,
    useGetQuery,
    MutateFormComponent,
    dialogTitles,
    setEmptyFilterParams,
    mutateFormProps,
}: IResultListProps<TFilterQueryParams, TListFieldsWithTitles, TFormFieldsWithTitles>) {
    // ensure the params have minimum length
    Object.keys(params).forEach(
        (key) => params[key]?.length && params[key]?.length < searchStringMinLength && delete params[key]
    );
    // get the data
    const {data, error, isLoading} = useGetQuery({...params, limit: resultListMaxRows});

    // state for the modals
    const [isMutateModalVisible, setIsMutateModalVisible] = useState(false);
    const [defaultObject, setDefaultObject] = useState(undefined);

    // action for the row click
    const editFn = (e, rowObject) => {
        e.preventDefault();
        setIsMutateModalVisible(true);
        setDefaultObject(rowObject);
    };

    // To decide if the row is clickable
    const isModify = !!(dialogTitles && "modify" in dialogTitles);
    const itemClassName = isModify ? "results-list__item" : "results-list__no-mod-item";

    // To decide whether to show the create new -button
    const isNew = !!(dialogTitles && "new" in dialogTitles);

    // Function the check if an object has property "non_disclosure" set to true
    const isObfuscated = (obj: TDefaultObject) => {
        return "non_disclosure" in obj && obj["non_disclosure"] === true;
    };

    return (
        <QueryStateHandler
            data={data}
            error={error}
            isLoading={isLoading}
        >
            <div className="list-headers">
                {Object.entries(listFieldsWithTitles).map(([field, title]) => (
                    <div key={field}>{title}</div>
                ))}
            </div>
            <div className="results-list">
                {data?.contents.map((rowObject: TDefaultObject) => (
                    <div
                        key={rowObject["id"]}
                        className={itemClassName}
                        {...(isModify && {onClick: (e) => editFn(e, rowObject)})}
                    >
                        {Object.keys(listFieldsWithTitles).map((field) => (
                            <span key={field}>
                                {isObfuscated(rowObject) && field === "name"
                                    ? "*** " + rowObject[field]
                                    : rowObject[field]}
                            </span>
                        ))}
                    </div>
                ))}
            </div>
            <div className="list-footer">
                <div className="list-footer-item">
                    Näytetään {data?.page.size}/{data?.page.total_items} hakutulosta
                </div>
                {isNew && (
                    <div className="list-footer-item">
                        <Button
                            theme="black"
                            iconLeft={<IconPlus />}
                            onClick={() => setIsMutateModalVisible(true)}
                        >
                            Luo uusi
                        </Button>
                    </div>
                )}
            </div>
            <MutateModal
                defaultObject={isMutateModalVisible ? defaultObject : undefined}
                MutateFormComponent={MutateFormComponent}
                dialogTitles={dialogTitles}
                isVisible={isMutateModalVisible}
                closeModalAction={() => {
                    setIsMutateModalVisible(false);
                    setDefaultObject(undefined);
                }}
                setEmptyFilterParams={setEmptyFilterParams}
                mutateFormProps={mutateFormProps}
            />
        </QueryStateHandler>
    );
}

interface IMutateSearchListProps<
    TListFieldsWithTitles extends object,
    TFilterQueryParams extends object,
    TFilterTitles extends object,
    TFormFieldsWithTitles extends object,
> {
    listFieldsWithTitles: TListFieldsWithTitles;
    searchStringMinLength?: number;
    resultListMaxRows?: number;
    useGetQuery;
    emptyFilterParams: TFilterQueryParams;
    filterTitles?: TFilterTitles;
    dialogTitles?: {modify?: string; new?: string};
    MutateFormComponent;
    mutateFormProps?: IMutateFormProps<TFormFieldsWithTitles>;
}

/* Generic list for searching data and for opening modal to add or modify the data
 *  - Modification or addition is enabled only if the corresponding dialogTitles -property is defined
 *  - Search fields are created for all emptyFilterParams -fields */
export default function MutateSearchList<
    TListFieldsWithTitles extends object,
    TFilterQueryParams extends object,
    TFilterTitles extends object,
    TFormFieldsWithTitles extends object,
>({
    listFieldsWithTitles,
    searchStringMinLength = 2,
    resultListMaxRows = 12,
    useGetQuery,
    MutateFormComponent,
    emptyFilterParams,
    filterTitles,
    dialogTitles,
    mutateFormProps,
}: IMutateSearchListProps<TListFieldsWithTitles, TFilterQueryParams, TFilterTitles, TFormFieldsWithTitles>) {
    // search strings
    const [filterParams, setFilterParams] = useState<TFilterQueryParams>(emptyFilterParams);

    // focus the field when clicking its cross circle icon
    const ref = useRef({});
    const focus = useCallback(
        (field: string) => {
            ref.current[field]?.focus();
        },
        [ref]
    );
    const clearAndFocus = (field: string) => {
        setFilterParams((prev) => ({...prev, [field]: ""}));
        focus(field);
    };

    return (
        <div className="listing">
            <div className="filters">
                {Object.entries(emptyFilterParams).map(([field, _defaultValue], i) => (
                    <TextInput
                        key={field}
                        id="filter__name"
                        ref={(element) => (ref.current[field] = element)}
                        label={(filterTitles?.[field] ?? "") as string}
                        value={filterParams[field]}
                        onChange={(e) => setFilterParams((prev) => ({...prev, [field]: e.target.value}))}
                        onButtonClick={() => clearAndFocus(field)}
                        autoFocus={i === 0} // Focus first field
                        buttonIcon={filterParams[field] ? <IconCrossCircle /> : <IconSearch />}
                    />
                ))}
            </div>
            <ResultList
                params={filterParams}
                searchStringMinLength={searchStringMinLength}
                resultListMaxRows={resultListMaxRows}
                useGetQuery={useGetQuery}
                MutateFormComponent={MutateFormComponent}
                dialogTitles={dialogTitles}
                listFieldsWithTitles={listFieldsWithTitles}
                setEmptyFilterParams={() => setFilterParams(emptyFilterParams)}
                mutateFormProps={mutateFormProps}
            />
        </div>
    );
}
