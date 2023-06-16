import {Button, IconCrossCircle, IconPlus, IconSearch, TextInput} from "hds-react";
import React, {useCallback, useRef, useState} from "react";
import {MutateModal, QueryStateHandler} from "../../common/components";

interface IResultListProps<TFilterQueryParams extends object, TListFieldsWithTitles extends object> {
    listFieldsWithTitles: TListFieldsWithTitles;
    params: TFilterQueryParams;
    searchStringMinLength: number;
    resultListMaxRows: number;
    useGetQuery;
    MutateFormComponent: React.FC<{defaultObject?: TListFieldsWithTitles; closeModalAction: () => void}>;
    dialogTitles?: {modify?: string; new?: string};
    setDefaultFilterParams?: () => void;
}

function ResultList<
    TFilterQueryParams extends object,
    TDefaultObject extends object,
    TListFieldsWithTitles extends object
>({
    listFieldsWithTitles,
    params,
    searchStringMinLength,
    resultListMaxRows,
    useGetQuery,
    MutateFormComponent,
    dialogTitles,
    setDefaultFilterParams,
}: IResultListProps<TFilterQueryParams, TListFieldsWithTitles>) {
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
    const editFn = (rowObject) => {
        setIsMutateModalVisible(true);
        setDefaultObject(rowObject);
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
            <ul className="results-list">
                {data?.contents.map((rowObject: TDefaultObject) => (
                    <div
                        key={rowObject["id"]}
                        className="results-list__item"
                        onClick={(e) => {
                            e.preventDefault();
                            editFn(rowObject);
                        }}
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
                <div className="list-footer-item">
                    <Button
                        theme="black"
                        iconLeft={<IconPlus />}
                        onClick={() => setIsMutateModalVisible(true)}
                    >
                        Luo uusi
                    </Button>
                </div>
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
                setDefaultFilterParams={setDefaultFilterParams}
            />
        </QueryStateHandler>
    );
}

interface IMutateSearchListProps<TListFieldsWithTitles extends object, TFilterQueryParams extends object> {
    listFieldsWithTitles: TListFieldsWithTitles;
    searchStringMinLength: number;
    resultListMaxRows: number;
    useGetQuery;
    MutateFormComponent: React.FC<{defaultObject?: TListFieldsWithTitles; closeModalAction: () => void}>;
    defaultFilterParams: TFilterQueryParams;
    dialogTitles?: {modify?: string; new?: string};
}

export default function MutateSearchList<TListFieldsWithTitles extends object, TFilterQueryParams extends object>({
    listFieldsWithTitles,
    searchStringMinLength,
    resultListMaxRows,
    useGetQuery,
    MutateFormComponent,
    defaultFilterParams,
    dialogTitles,
}: IMutateSearchListProps<TListFieldsWithTitles, TFilterQueryParams>) {
    // search strings
    const [filterParams, setFilterParams] = useState<TFilterQueryParams>(defaultFilterParams);

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
                {Object.entries(listFieldsWithTitles).map(([field, title], i) => (
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
                setDefaultFilterParams={() => setFilterParams(defaultFilterParams)}
            />
        </div>
    );
}
