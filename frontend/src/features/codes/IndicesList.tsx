import React, {useEffect, useState} from "react";

import {Button, Dialog, IconPlus, Select} from "hds-react";
import {useImmer} from "use-immer";

import {useForm} from "react-hook-form";
import {useGetIndicesQuery, useSaveIndexMutation} from "../../app/services";
import {QueryStateHandler, SaveButton} from "../../common/components";
import {FilterTextInputField} from "../../common/components/filters";
import {NumberInput, TextInput} from "../../common/components/form";
import {IIndex} from "../../common/schemas";
import {hdsToast} from "../../common/utils";

const indexOptions: {label: string; value: string}[] = [
    {label: "Markkinahintaindeksi 1983", value: "market-price-index"},
    {label: "Markkinahintaindeksi 2005", value: "market-price-index-2005-equal-100"},
    {label: "Rakennuskustannusindeksi 1980", value: "construction-price-index"},
    {label: "Rakennuskustannusindeksi 2005", value: "construction-price-index-2005-equal-100"},
    {label: "Rajaneliöhinta", value: "surface-area-price-ceiling"},
    {label: "Luovutushintaindeksi", value: "maximum-price-index"},
];

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

const LoadedIndexResultsList = ({data, editFn}) => {
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

const IndexResultList = ({setFormData, setCreateDialogOpen, indexType, filterParams}) => {
    const {data, error, isLoading} = useGetIndicesQuery({
        indexType: indexType.value,
        params: {
            ...filterParams,
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
                />
            </QueryStateHandler>
        </div>
    );
};

const IndicesList = (): React.JSX.Element => {
    const initialSaveData: IIndex = {
        indexType: indexOptions[0].value,
        month: `${new Date().getFullYear()}-${("0" + (new Date().getMonth() + 1)).slice(-2)}`,
        value: null,
    };

    const [filterParams, setFilterParams] = useState({});
    const [currentIndexType, setCurrentIndexType] = useState(indexOptions[0]);

    const [formData, setFormData] = useImmer(initialSaveData);
    const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

    const closeModal = () => {
        setFormData(initialSaveData);
        setIsModalOpen(false);
    };

    return (
        <div className="listing">
            <div className="filters">
                <Select
                    label="Indeksityyppi"
                    options={indexOptions}
                    onChange={(selected) => setCurrentIndexType(selected)}
                    defaultValue={indexOptions[0]}
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
                isModalOpen={isModalOpen}
                closeModal={closeModal}
            />
        </div>
    );
};

const EditIndexModal = ({indexType, formData, isModalOpen, closeModal}) => {
    const [saveIndex, {data, error, isLoading}] = useSaveIndexMutation();
    const editIndexForm = useForm({
        defaultValues: formData,
        mode: "all",
    });
    const {handleSubmit} = editIndexForm;
    const handleSaveIndex = () => {
        saveIndex({
            data: formData,
            index: indexType.value,
            month: formData.month,
        });
    };

    useEffect(() => {
        if (isLoading || !data) return;
        if (data && !error) {
            hdsToast.success("Indeksi tallennettu onnistuneesti");
            editIndexForm.reset();
            closeModal();
        } else {
            hdsToast.error("Indeksin tallennus epäonnistui");
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
                title={`Tallenna ${indexType.label}`}
            />
            <form onSubmit={handleSubmit(handleSaveIndex)}>
                <Dialog.Content>
                    <TextInput
                        label="Kuukausi (VVVV-KK)"
                        name="month"
                        formObject={editIndexForm}
                        tooltipText="Esim 2022-12"
                        required
                    />
                    <NumberInput
                        label="Arvo"
                        allowDecimals={true}
                        name="value"
                        formObject={editIndexForm}
                        required
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
                        type="submit"
                        isLoading={isLoading}
                    />
                </Dialog.ActionButtons>
            </form>
        </Dialog>
    );
};

export default IndicesList;
