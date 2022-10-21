import React, {useEffect, useState} from "react";

import {Button, Dialog, IconPlus, LoadingSpinner, Select} from "hds-react";
import {useImmer} from "use-immer";

import {useGetIndicesQuery, useSaveIndexMutation} from "../../app/services";
import {FilterTextInputField, FormInputField, ListPageNumbers} from "../../common/components";
import {IIndex} from "../../common/models";
import {hitasToast} from "../../common/utils";

const indexTypes: {label: string}[] = [
    {label: "max-price-index"},
    {label: "market-price-index"},
    {label: "market-price-index-2005-equal-100"},
    {label: "construction-price-index"},
    {label: "construction-price-index-2005-equal-100"},
    {label: "surface-area-price-ceiling"},
];
const getIndexTypeName = (indexType: string): string => {
    switch (indexType) {
        case "max-price-index":
            return "enimmäishintaindeksi";
        case "market-price-index":
            return "markkinahintaindeksi";
        case "market-price-index-2005-equal-100":
            return "markkinahintaindeksi (ennen v. 2005)";
        case "construction-price-index":
            return "rakennushintaindeksi";
        case "construction-price-index-2005-equal-100":
            return "rakennushintaindeksi (ennen v. 2005)";
        case "surface-area-price-ceiling":
            return "rajaneliöhintaindeksi";
        default:
            return "VIRHE";
    }
};
const indexOptions = indexTypes.map(({label}) => {
    return {label: getIndexTypeName(label), value: label};
});

const IndicesList = (): JSX.Element => {
    const [editMonth, setEditMonth] = useState<string | null>(null);
    const [editValue, setEditValue] = useState<number | null>(null);
    const initialSaveData: IIndex = {
        indexType: indexTypes[0].label,
        month: editMonth || "",
        value: editValue || null,
    };
    const [formData, setFormData] = useImmer(initialSaveData);
    const [filterParams, setFilterParams] = useState({string: ""});
    const [editDialogOpen, setCreateDialogOpen] = useState<boolean>(false);
    const initData = () => {
        setEditMonth(null);
        setEditValue(null);
        setFormData(initialSaveData);
    };
    const closeDialog = () => {
        initData();
        setCreateDialogOpen(false);
    };
    const [currentPage, setCurrentPage] = useState(1);
    const [currentIndexType, setCurrentIndexType] = useState(indexTypes[0]);
    const {
        data: results,
        error,
        isLoading,
    } = useGetIndicesQuery({
        ...filterParams,
        page: currentPage,
        indexType: currentIndexType.label,
    });

    const LoadedIndexResultsList = () => {
        return (
            <div className="results">
                {error ? (
                    <span>Virhe</span>
                ) : results?.contents.length ? (
                    <>
                        <div className="list-headers">
                            <div className="list-header month">Kuukausi</div>
                            <div className="list-header value">Arvo</div>
                        </div>
                        <ul className="results-list">
                            {results?.contents.map((item: IIndex) => (
                                <IndexListItem
                                    key={item.month}
                                    month={item.month}
                                    value={item.value as number}
                                />
                            ))}
                        </ul>
                    </>
                ) : (
                    <div>Ei löytynyt yhtään "{getIndexTypeName(currentIndexType.label)}" tyyppistä indeksiä.</div>
                )}
                <ListPageNumbers
                    currentPage={currentPage}
                    setCurrentPage={setCurrentPage}
                    pageInfo={results?.page}
                />
            </div>
        );
    };

    const IndexListItem = ({month, value}: {month: string; value: number}) => (
        <div
            className="results-list__item results-list__item--code"
            onClick={(e) => {
                e.preventDefault();
                setFormData({indexType: currentIndexType.label, month: month, value: value});
                setCreateDialogOpen(true);
            }}
        >
            <span className="month">{month}</span>
            <span className="value">{value}</span>
        </div>
    );
    const onSelectionChange = ({value}) => {
        setEditMonth(null);
        setEditValue(null);
        setCurrentIndexType(() => ({label: value}));
    };
    function result() {
        return (
            <div className="listing">
                {!isLoading ? (
                    <>
                        <div className="filters">
                            <Select
                                label={"Indeksityyppi"}
                                options={indexOptions}
                                onChange={onSelectionChange}
                                defaultValue={{
                                    value: indexTypes[0].label,
                                    label: getIndexTypeName(indexTypes[0].label),
                                }}
                            />
                            <div style={{display: "none"}}>
                                <FilterTextInputField
                                    label="Kuukausi"
                                    filterFieldName="month"
                                    filterParams={filterParams}
                                    setFilterParams={setFilterParams}
                                />
                            </div>
                        </div>
                        <EditIndexDialog
                            editDialogOpen={editDialogOpen}
                            closeDialog={closeDialog}
                            indexType={currentIndexType}
                            formData={formData}
                            setFormData={setFormData}
                        />
                        <LoadedIndexResultsList />
                        <div className={"index-actions"}>
                            <Button
                                theme="black"
                                iconLeft={<IconPlus />}
                                onClick={() => setCreateDialogOpen(true)}
                            >
                                Lisää/päivitä indeksi
                            </Button>
                        </div>
                    </>
                ) : (
                    <LoadingSpinner />
                )}
            </div>
        );
    }

    return result();
};

const EditIndexDialog = ({indexType, formData, setFormData, editDialogOpen, closeDialog}) => {
    const [saveIndex, {data: saveData, error: saveError, isLoading: isSaving}] = useSaveIndexMutation();
    const handleSaveIndex = () => {
        saveIndex({
            data: formData,
            index: formData.indexType as string,
            month: formData.month,
        });
        closeDialog();
    };
    useEffect(() => {
        if (isSaving) return;
        if (saveData) {
            hitasToast(
                saveError ? "Indeksin tallennus epäonnistui" : "Indeksi tallennettu onnistuneesti",
                saveError ? "error" : "success"
            );
        }
    }, [isSaving, saveError, saveData]);
    return isSaving ? (
        <LoadingSpinner />
    ) : (
        <Dialog
            id="index-creation-dialog"
            aria-labelledby={"create-modal"}
            isOpen={editDialogOpen}
            close={() => closeDialog()}
            closeButtonLabelText={"Sulje"}
            boxShadow={true}
        >
            <Dialog.Header
                id="index-creation-header"
                title={"Tallenna " + getIndexTypeName(indexType.label)}
            />
            <Dialog.Content>
                <FormInputField
                    label={"Kuukausi"}
                    fieldPath={"month"}
                    formData={formData}
                    setFormData={setFormData}
                    error={saveError}
                    tooltipText={"Muodossa VVVV-KK, esim 2022-12"}
                />
                <FormInputField
                    label={"Arvo"}
                    inputType={"number"}
                    fieldPath={"value"}
                    formData={formData}
                    setFormData={setFormData}
                    error={saveError}
                />
            </Dialog.Content>
            <Dialog.ActionButtons>
                <Button
                    onClick={() => closeDialog()}
                    theme={"black"}
                    variant={"secondary"}
                >
                    Peruuta
                </Button>
                <Button
                    onClick={handleSaveIndex}
                    theme={"black"}
                >
                    Tallenna
                </Button>
            </Dialog.ActionButtons>
        </Dialog>
    );
};

export default IndicesList;
