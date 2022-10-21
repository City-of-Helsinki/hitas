import React, {useEffect, useState} from "react";

import {Button, Dialog, IconPlus, LoadingSpinner, Select} from "hds-react";
import {useImmer} from "use-immer";

import {useGetIndicesQuery, useSaveIndexMutation} from "../../app/services";
import {FormInputField, ListPageNumbers, QueryStateHandler} from "../../common/components";
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
            return "Enimmäishintaindeksi";
        case "market-price-index":
            return "Markkinahintaindeksi (ennen 2005)";
        case "market-price-index-2005-equal-100":
            return "Markkinahintaindeksi (2005 eteenpäin)";
        case "construction-price-index":
            return "Rakennuskustannusindeksi (ennen 2005)";
        case "construction-price-index-2005-equal-100":
            return "Rakennuskustannusindeksi (2005 eteenpäin)";
        case "surface-area-price-ceiling":
            return "Rajaneliöhinta";
        default:
            return "VIRHE";
    }
};
const indexOptions = indexTypes.map(({label}) => {
    return {label: getIndexTypeName(label), value: label};
});

const IndexListItem = ({month, value, editFn}: {month: string; value: number; editFn}) => (
    <div
        className="results-list__item results-list__item--code"
        onClick={(e) => {
            e.preventDefault();
            editFn({month: month, value: value});
        }}
    >
        <span className="month">{month}</span>
        <span className="value">{value}</span>
    </div>
);

const LoadedIndexResultsList = ({data, editFn, currentPage}) => {
    return (
        <div className="results">
            {data.page.total_pages > 1 && (
                <div className={"results__page-counter"}>
                    Sivu {currentPage} / {data.page.total_pages}
                </div>
            )}
            <div className="list-headers">
                <div className="list-header month">Kuukausi</div>
                <div className="list-header value">Arvo</div>
            </div>
            <ul className="results-list">
                {data?.contents.map((item: IIndex) => (
                    <IndexListItem
                        key={item.month}
                        month={item.month}
                        value={item.value as number}
                        editFn={editFn}
                    />
                ))}
            </ul>
        </div>
    );
};

const IndexResultList = ({setFormData, setCreateDialogOpen, indexType}) => {
    const [currentPage, setCurrentPage] = useState(1);
    const {data, error, isLoading} = useGetIndicesQuery({
        indexType: indexType.label,
        params: {
            page: currentPage,
            limit: 12,
        },
    });
    return (
        <div className="results">
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                {!isLoading && !error ? (
                    <>
                        <LoadedIndexResultsList
                            data={data}
                            editFn={({month, value}) => {
                                setFormData({
                                    indexType: indexType,
                                    month: month,
                                    value: value,
                                });
                                setCreateDialogOpen(true);
                            }}
                            currentPage={currentPage}
                        />
                        <ListPageNumbers
                            currentPage={currentPage}
                            setCurrentPage={setCurrentPage}
                            pageInfo={data?.page}
                        />
                    </>
                ) : (
                    <LoadingSpinner />
                )}
            </QueryStateHandler>
            <></>
        </div>
    );
};

const IndicesList = (): JSX.Element => {
    const [currentIndexType, setCurrentIndexType] = useState(indexTypes[0]);
    const [editMonth, setEditMonth] = useState<string | null>(null);
    const [editValue, setEditValue] = useState<number | null>(null);
    const initialSaveData: IIndex = {
        indexType: indexTypes[0].label,
        month: editMonth || "",
        value: editValue || null,
    };
    const [formData, setFormData] = useImmer(initialSaveData);
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
    const onSelectionChange = ({value}) => {
        setEditMonth(null);
        setEditValue(null);
        setCurrentIndexType(() => ({label: value}));
    };
    return (
        <div className="listing">
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
            </div>
            <IndexResultList
                indexType={currentIndexType}
                setFormData={setFormData}
                setCreateDialogOpen={setCreateDialogOpen}
            />
            <div className={"index-actions"}>
                <Button
                    theme="black"
                    iconLeft={<IconPlus />}
                    onClick={() => setCreateDialogOpen(true)}
                >
                    Lisää/päivitä indeksi
                </Button>
            </div>
            <EditIndexDialog
                editDialogOpen={editDialogOpen}
                closeDialog={closeDialog}
                indexType={currentIndexType}
                formData={formData}
                setFormData={setFormData}
            />
        </div>
    );
};

const EditIndexDialog = ({indexType, formData, setFormData, editDialogOpen, closeDialog}) => {
    const [saveIndex, {data: saveData, error: saveError, isLoading: isSaving}] = useSaveIndexMutation();
    const handleSaveIndex = () => {
        saveIndex({
            data: formData,
            index: indexType as string,
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
                title={"Tallenna " + getIndexTypeName(indexType.label).toLowerCase()}
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
