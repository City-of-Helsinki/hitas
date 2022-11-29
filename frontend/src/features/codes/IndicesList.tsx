import React, {useEffect, useState} from "react";

import {Button, Dialog, IconPlus, Select} from "hds-react";
import {useImmer} from "use-immer";

import {useGetIndicesQuery, useSaveIndexMutation} from "../../app/services";
import {FilterTextInputField, FormInputField, QueryStateHandler, SaveButton} from "../../common/components";
import {IIndex} from "../../common/models";
import {hitasToast} from "../../common/utils";

const indexTypes: {label: string}[] = [
    {label: "market-price-index"},
    {label: "market-price-index-2005-equal-100"},
    {label: "construction-price-index"},
    {label: "construction-price-index-2005-equal-100"},
    {label: "surface-area-price-ceiling"},
    {label: "maximum-price-index"},
];
const getIndexTypeName = (indexType: string): string => {
    switch (indexType) {
        case "maximum-price-index":
            return "Luovutushintaindeksi";
        case "market-price-index":
            return "Markkinahintaindeksi 1983";
        case "market-price-index-2005-equal-100":
            return "Markkinahintaindeksi 2005";
        case "construction-price-index":
            return "Rakennuskustannusindeksi 1980";
        case "construction-price-index-2005-equal-100":
            return "Rakennuskustannusindeksi 2005";
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

const IndexResultList = ({currentPage, setFormData, setCreateDialogOpen, indexType, filterParams}) => {
    const {data, error, isLoading} = useGetIndicesQuery({
        indexType: indexType.label,
        params: {
            ...filterParams,
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
            </QueryStateHandler>
        </div>
    );
};

const todaysDate = new Date();
const initialSaveData: IIndex = {
    indexType: indexTypes[0].label,
    month: `${todaysDate.getFullYear()}-${("0" + (todaysDate.getMonth() + 1)).slice(-2)}`,
    value: null,
};

const IndicesList = (): JSX.Element => {
    const [filterParams, setFilterParams] = useState({});
    const [currentIndexType, setCurrentIndexType] = useState(indexTypes[0]);
    const [currentPage, setCurrentPage] = useState(1);
    const [formData, setFormData] = useImmer(initialSaveData);
    const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

    const closeModal = () => {
        setFormData(initialSaveData);
        setIsModalOpen(false);
    };
    const onSelectionChange = ({value}) => {
        setCurrentPage(1);
        setCurrentIndexType(() => ({label: value}));
    };

    return (
        <div className="listing">
            <div className="filters">
                <Select
                    label="Indeksityyppi"
                    options={indexOptions}
                    onChange={onSelectionChange}
                    defaultValue={{
                        value: indexTypes[0].label,
                        label: getIndexTypeName(indexTypes[0].label),
                    }}
                />
                <FilterTextInputField
                    label="Vuosi"
                    filterFieldName="year"
                    filterParams={filterParams}
                    setFilterParams={setFilterParams}
                    minLength={4}
                    maxLength={4}
                />
            </div>
            <IndexResultList
                currentPage={currentPage}
                indexType={currentIndexType}
                setFormData={setFormData}
                setCreateDialogOpen={setIsModalOpen}
                filterParams={filterParams}
            />
            <div className="index-actions">
                <Button
                    theme="black"
                    iconLeft={<IconPlus />}
                    onClick={() => setIsModalOpen(true)}
                >
                    Lisää/päivitä indeksi
                </Button>
            </div>
            <EditIndexModal
                indexType={currentIndexType}
                formData={formData}
                setFormData={setFormData}
                isModalOpen={isModalOpen}
                closeModal={closeModal}
            />
        </div>
    );
};

const EditIndexModal = ({indexType, formData, setFormData, isModalOpen, closeModal}) => {
    const [saveIndex, {data, error, isLoading}] = useSaveIndexMutation();
    const handleSaveIndex = () => {
        saveIndex({
            data: formData,
            index: indexType.label,
            month: formData.month,
        });
    };

    useEffect(() => {
        if (isLoading || !data) return;
        if (data && !error) {
            hitasToast("Indeksi tallennettu onnistuneesti", "success");
            closeModal();
        } else {
            hitasToast("Indeksin tallennus epäonnistui", "error");
        }
        // eslint-disable-next-line
    }, [isLoading, error, data]);

    return (
        <Dialog
            id="index-creation-dialog"
            aria-labelledby="create-modal"
            isOpen={isModalOpen}
            close={() => closeModal()}
            closeButtonLabelText="Sulje"
            boxShadow
        >
            <Dialog.Header
                id="index-creation-header"
                title={"Tallenna " + getIndexTypeName(indexType.label).toLowerCase()}
            />
            <Dialog.Content>
                <FormInputField
                    label="Kuukausi"
                    fieldPath="month"
                    formData={formData}
                    setFormData={setFormData}
                    error={error}
                    tooltipText="Esim 2022-12"
                />
                <FormInputField
                    label="Arvo"
                    inputType="number"
                    fractionDigits={2}
                    fieldPath="value"
                    formData={formData}
                    setFormData={setFormData}
                    error={error}
                />
            </Dialog.Content>
            <Dialog.ActionButtons>
                <Button
                    onClick={() => closeModal()}
                    theme="black"
                    variant="secondary"
                >
                    Peruuta
                </Button>
                <SaveButton
                    onClick={handleSaveIndex}
                    isLoading={isLoading}
                />
            </Dialog.ActionButtons>
        </Dialog>
    );
};

export default IndicesList;
