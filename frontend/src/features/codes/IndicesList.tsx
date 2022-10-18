import React, {useEffect, useState} from "react";

import {Button, Dialog, IconPlus, LoadingSpinner, Select} from "hds-react";
import {useImmer} from "use-immer";

import {useGetIndicesQuery, useSaveIndexMutation} from "../../app/services";
import {FilterTextInputField, FormInputField, ListPageNumbers} from "../../common/components";
import {IIndex} from "../../common/models";
import {hitasToast} from "../../common/utils";

const indices: {label: string}[] = [
    {label: "max-price-index"},
    {label: "market-price-index"},
    {label: "market-price-index-2005-equal-100"},
    {label: "construction-price-index"},
    {label: "construction-price-index-2005-equal-100"},
    {label: "surface-area-price-ceiling"},
];
const getIndexName = (indexType: string): string => {
    switch (indexType) {
        case "max-price-index":
            return "Enimmäishintaindeksi";
        case "market-price-index":
            return "Markkinahintaindeksi";
        case "market-price-index-2005-equal-100":
            return "Markkinahintaindeksi (ennen 2005)";
        case "construction-price-index":
            return "Rakennushintaindeksi";
        case "construction-price-index-2005-equal-100":
            return "Rakennushintaindeksi (ennen 2005)";
        case "surface-area-price-ceiling":
            return "Rajaneliöhinta";
        default:
            return "VIRHE";
    }
};
const indexOptions = indices.map(({label}) => {
    return {label: getIndexName(label), value: label};
});

const IndicesList = (): JSX.Element => {
    const [filterParams, setFilterParams] = useState({string: ""});
    const [createDialogOpen, setCreateDialogOpen] = useState<boolean>(false);
    const closeDialog = () => setCreateDialogOpen(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [currentIndex, setCurrentIndex] = useState(indices[0]);
    const {
        data: results,
        error,
        isLoading,
    } = useGetIndicesQuery({
        ...filterParams,
        page: currentPage,
        indexType: currentIndex.label,
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
                                    index={item.index}
                                    month={item.month}
                                    value={item.value}
                                />
                            ))}
                        </ul>
                    </>
                ) : (
                    <div>Ei tuloksia!</div>
                )}
            </div>
        );
    };

    const IndexListItem = ({month, value}: IIndex) => (
        <div className="results-list__item results-list__item--code">
            <span className="month">{month}</span>
            <span className="value">{value}</span>
        </div>
    );
    const onSelectionChange = ({value}) => {
        setCurrentIndex(() => {
            return {label: value};
        });
    };
    function result() {
        return (
            <div className="listing">
                {!isLoading ? (
                    <>
                        <div className="filters">
                            <Select
                                label={"Indeksi"}
                                options={indexOptions}
                                onChange={onSelectionChange}
                                defaultValue={{value: indices[0].label, label: getIndexName(indices[0].label)}}
                            />
                            <div style={{display: "none"}}>
                                <FilterTextInputField
                                    label="Kuukausi"
                                    filterFieldName="month"
                                    filterParams={filterParams}
                                    setFilterParams={setFilterParams}
                                />
                            </div>
                            <div className={"index-actions"}>
                                <div className="list-amount">{`Löytyi ${results?.page.total_items}kpl tuloksia`}</div>
                                <Button
                                    theme="black"
                                    iconLeft={<IconPlus />}
                                    onClick={() => setCreateDialogOpen(true)}
                                >
                                    Lisää indeksi
                                </Button>
                            </div>
                        </div>
                        <IndexCreateDialog
                            createDialogOpen={createDialogOpen}
                            closeDialog={closeDialog}
                            setCreateDialogOpen={setCreateDialogOpen}
                        />
                        <LoadedIndexResultsList />
                        <ListPageNumbers
                            currentPage={currentPage}
                            setCurrentPage={setCurrentPage}
                            pageInfo={results?.page}
                        />
                    </>
                ) : (
                    <LoadingSpinner />
                )}
            </div>
        );
    }

    return result();
};

const IndexCreateDialog = ({createDialogOpen, closeDialog, setCreateDialogOpen}) => {
    const initialSaveData: IIndex = {index: indices[0].label, month: "", value: null};
    const [formData, setFormData] = useImmer(initialSaveData);
    const [saveIndex, {data: saveData, error: saveError, isLoading: isSaving}] = useSaveIndexMutation();
    const handleSaveIndex = () => {
        saveIndex({
            data: formData,
            index: formData.index,
            month: formData.month,
        });
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
            isOpen={createDialogOpen}
            close={closeDialog}
            closeButtonLabelText={"Sulje"}
            boxShadow={true}
        >
            <Dialog.Header
                id="index-creation-header"
                title={`Uusi indeksi`}
            />
            <Dialog.Content>
                <FormInputField
                    inputType={"select"}
                    options={indexOptions}
                    defaultValue={indexOptions[0]}
                    label={"Indeksi"}
                    fieldPath={"index"}
                    formData={formData}
                    setFormData={setFormData}
                    error={saveError}
                />
                <FormInputField
                    label={"Kuukausi"}
                    fieldPath={"month"}
                    formData={formData}
                    setFormData={setFormData}
                    error={saveError}
                />
                <FormInputField
                    label={"Arvo"}
                    fieldPath={"value"}
                    formData={formData}
                    setFormData={setFormData}
                    error={saveError}
                />
            </Dialog.Content>
            <Dialog.ActionButtons>
                <Button
                    onClick={() => {
                        setCreateDialogOpen(false);
                    }}
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
