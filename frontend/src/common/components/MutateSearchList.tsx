import {Button, IconCrossCircle, IconPlus, IconSearch, TextInput} from "hds-react";
import {useCallback, useRef, useState} from "react";
import {MutateForm, MutateModal, QueryStateHandler} from "./";
interface IResultListProps<
    TFilterQueryParams extends object,
    TListFieldsWithTitles extends object,
    TFormFieldsWithTitles extends object
> {
    listFieldsWithTitles: TListFieldsWithTitles;
    params: TFilterQueryParams;
    searchStringMinLength: number;
    resultListMaxRows: number;
    useGetQuery;
    MutateFormComponent;
    dialogTitles?: {modify?: string; new?: string};
    setEmptyFilterParams?: () => void;
    isMutateForm: boolean;
    useSaveMutation?;
    formObjectSchema?;
    successMessage?: string;
    errorMessage?: string;
    notModifiedMessage?: string;
    defaultFocusFieldName?: string;
    formFieldsWithTitles?: TFormFieldsWithTitles;
    requiredFields?: string[];
}

function ResultList<
    TFilterQueryParams extends object,
    TDefaultObject extends object,
    TListFieldsWithTitles extends object,
    TFormFieldsWithTitles extends object
>({
    listFieldsWithTitles,
    params,
    searchStringMinLength,
    resultListMaxRows,
    useGetQuery,
    MutateFormComponent,
    dialogTitles,
    setEmptyFilterParams,
    isMutateForm,
    formObjectSchema,
    useSaveMutation,
    successMessage,
    errorMessage,
    notModifiedMessage,
    defaultFocusFieldName,
    formFieldsWithTitles,
    requiredFields,
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

    // generic MutateForm component -specific props
    const mutateFormProps = {
        formObjectSchema,
        useSaveMutation,
        successMessage,
        errorMessage,
        notModifiedMessage,
        defaultFocusFieldName,
        formFieldsWithTitles,
        requiredFields,
    };

    // To decide if the row is clickable
    const isModify = dialogTitles && "modify" in dialogTitles ? true : false;
    const itemClassName = isModify ? "results-list__item" : "results-list__no-mod-item";

    // To decide whether to show the create new -button
    const isNew = dialogTitles && "new" in dialogTitles ? true : false;

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
            <ul className="results-list">
                {data?.contents.map((rowObject: TDefaultObject) => (
                    <div
                        key={rowObject["id"]}
                        className={itemClassName}
                        {...(isModify && {onClick: (e) => editFn(e, rowObject)})}
                    >
                        {Object.keys(listFieldsWithTitles).map((field) => (
                            <span key={field}>{rowObject[field]}</span>
                        ))}
                    </div>
                ))}
            </ul>
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
                {...(isMutateForm && mutateFormProps)}
            />
        </QueryStateHandler>
    );
}

interface IMutateSearchListProps<
    TListFieldsWithTitles extends object,
    TFilterQueryParams extends object,
    TFormFieldsWithTitles extends object
> {
    listFieldsWithTitles: TListFieldsWithTitles;
    searchStringMinLength: number;
    resultListMaxRows: number;
    useGetQuery;
    MutateFormComponent;
    emptyFilterParams: TFilterQueryParams;
    dialogTitles?: {modify?: string; new?: string};
    formObjectSchema?;
    useSaveMutation?;
    saveDataFunction?;
    isSaveDataLoading?: boolean;
    successMessage?: string;
    errorMessage?: string;
    notModifiedMessage?: string;
    defaultFocusFieldName?: string;
    formFieldsWithTitles?: TFormFieldsWithTitles;
    requiredFields?: string[];
}

/* Generic list for searching data and for opening modal to add or modify the data
 *  - Modification or addition is enabled only if the corresponding dialogTitles -property is defined
 *  - Search fields are created for all emptyFilterParams -fields */
export default function MutateSearchList<
    TListFieldsWithTitles extends object,
    TFilterQueryParams extends object,
    TFormFieldsWithTitles extends object
>({
    listFieldsWithTitles,
    searchStringMinLength,
    resultListMaxRows,
    useGetQuery,
    MutateFormComponent,
    emptyFilterParams,
    dialogTitles,
    formObjectSchema,
    useSaveMutation,
    successMessage,
    errorMessage,
    notModifiedMessage,
    defaultFocusFieldName,
    formFieldsWithTitles,
    requiredFields,
}: IMutateSearchListProps<TListFieldsWithTitles, TFilterQueryParams, TFormFieldsWithTitles>) {
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

    const mutateFormProps = {
        formObjectSchema,
        useSaveMutation,
        successMessage,
        errorMessage,
        notModifiedMessage,
        defaultFocusFieldName,
        formFieldsWithTitles,
        requiredFields,
    };

    // check if the MutateFormComponent is MutateForm
    const isMutateForm = (<MutateForm />).type === (<MutateFormComponent />).type;

    return (
        <div className="listing">
            <div className="filters">
                {Object.entries(emptyFilterParams).map(([field, title], i) => (
                    <TextInput
                        key={field}
                        id="filter__name"
                        ref={(element) => (ref.current[field] = element)}
                        label={title as string}
                        value={filterParams[field]}
                        onChange={(e) => setFilterParams((prev) => ({...prev, [field]: e.target.value}))}
                        onButtonClick={() => clearAndFocus(field)}
                        autoFocus={i === 0 ? true : false}
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
                isMutateForm={isMutateForm}
                {...(isMutateForm && mutateFormProps)}
            />
        </div>
    );
}
