import React, {useEffect, useState} from "react";

import {Button, Combobox, Dialog, IconPlus, IconSearch, LoadingSpinner} from "hds-react";
import {useImmer} from "use-immer";

import {useGetIndicesQuery, useSaveIndexMutation} from "../../app/services";
import {FilterTextInputField, FormInputField, ListPageNumbers} from "../../common/components";
import {IIndex, IIndexResponse, IndexType} from "../../common/models";
import {hitasToast} from "../../common/utils";

const indices: IndexType[] = [
    {label: "max-value-index"},
    {label: "market-price-index"},
    {label: "market-price-index-2005-equal-100"},
    {label: "construction-price-index"},
    {label: "construction-price-index-2005-equal-100"},
    {label: "surface-area-price-ceiling"},
];
const getIndexName = (state: string) => {
    switch (state) {
        case "max-value-index":
            return "Enimmäishintaindeksi";
        case "market-price-index":
            return "Markkinahintaindeksi";
        case "market-price-index-2005-equals-100":
            return "Markkinahintaindeksi (ennen 2005)";
        case "construction-price-index":
            return "Rakennushintaindeksi";
        case "construction-price-index-2005-equals-100":
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

const IndicesList = ({filterParams, setFilterParams}): JSX.Element => {
    const [createDialogOpen, setCreateDialogOpen] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [currentIndex, setCurrentIndex] = useState();
    const {
        data: results,
        error,
        isLoading,
    } = useGetIndicesQuery({
        ...filterParams,
        page: currentPage,
        indexType: indices[0].label,
    });
    const initialSaveData: IIndex = {index: indices[0], month: "", value: null};
    const [formData, setFormData] = useImmer(initialSaveData);
    const [saveIndex, {data: saveData, error: saveError, isLoading: isSaving}] = useSaveIndexMutation();
    const handleSaveIndex = () => {
        saveIndex({
            data: formData,
            index: formData.index.label,
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
    const LoadedIndexResultsList = ({data, dialogToggle}: {data: IIndexResponse; dialogToggle}) => {
        return (
            <div className="results">
                <div className="list-amount">{`Löytyi ${data.page.total_items}kpl tuloksia`}</div>
                <div className="list-headers">
                    <div className="list-header month">Kuukausi</div>
                    <div className="list-header value">Arvo</div>
                </div>
                <ul className="results-list">
                    <IndexListItem
                        index={indices[0]}
                        month={"2022-01"}
                        value={127.12}
                    />
                    <IndexListItem
                        index={indices[1]}
                        month={"2022-02"}
                        value={194.44}
                    />
                    <IndexListItem
                        index={indices[2]}
                        month={"2022-01"}
                        value={127.12}
                    />
                    <IndexListItem
                        index={indices[3]}
                        month={"2022-02"}
                        value={194.44}
                    />
                    <IndexListItem
                        index={indices[4]}
                        month={"2022-01"}
                        value={127.12}
                    />
                    <IndexListItem
                        index={indices[0]}
                        month={"2022-02"}
                        value={194.44}
                    />
                    {data.contents.map((item: IIndex) => (
                        <IndexListItem
                            key={item.month}
                            index={item.index}
                            month={item.month}
                            value={item.value}
                        />
                    ))}
                </ul>
                <Button
                    theme="black"
                    iconLeft={<IconPlus />}
                    onClick={() => dialogToggle(true)}
                >
                    Lisää indeksi
                </Button>
            </div>
        );
    };

    const IndexListItem = ({index, month, value}: IIndex) => {
        return (
            <div className="results-list__item results-list__item--code">
                <span className="index">{index.label}</span>
                <span className="month">{month}</span>
                <span className="value">{value}</span>
            </div>
        );
    };
    function result(
        data,
        error,
        isLoading,
        currentPage,
        setCurrentPage,
        currentIndex,
        setCurrentIndex,
        filterParams,
        setFilterParams,
        createDialogOpen,
        setCreateDialogOpen
    ) {
        const onSelectionChange = (value: {value: string}) => {
            setCurrentIndex(value.value);
        };
        return !isLoading ? (
            <div className="listing">
                <div className="search">
                    <FilterTextInputField
                        label=""
                        filterFieldName="display_name"
                        filterParams={filterParams}
                        setFilterParams={setFilterParams}
                    />
                    <IconSearch />
                </div>
                <LoadedIndexResultsList
                    data={data as IIndexResponse}
                    dialogToggle={setCreateDialogOpen}
                />
                <ListPageNumbers
                    currentPage={currentPage}
                    setCurrentPage={setCurrentPage}
                    pageInfo={data?.page}
                />
                <div className="filters">
                    <Combobox
                        label={"Indeksi"}
                        options={indexOptions}
                        toggleButtonAriaLabel={"Toggle menu"}
                        onChange={onSelectionChange}
                        clearable
                    />
                </div>
                <IndexCreateDialog
                    isOpen={createDialogOpen}
                    toggle={setCreateDialogOpen}
                />
            </div>
        ) : (
            <LoadingSpinner />
        );
    }
    const IndexCreateDialog = (createDialogOpen, setCreateDialogOpen) => {
        return (
            <Dialog
                id="index-creation-dialog"
                closeButtonLabelText={"args.closeButtonLabelText"}
                aria-labelledby={"create-modal"}
                isOpen={createDialogOpen}
                close={() => setCreateDialogOpen(false)}
                boxShadow={true}
            >
                <Dialog.Header
                    id="index-creation-header"
                    title={`Uusi indeksi`}
                />
                <Dialog.Content>
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
                        onClick={() => setCreateDialogOpen(false)}
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
    return result(
        results,
        error,
        isLoading,
        currentPage,
        setCurrentPage,
        currentIndex,
        setCurrentIndex,
        filterParams,
        setFilterParams,
        createDialogOpen,
        setCreateDialogOpen
    );
};

export default IndicesList;
