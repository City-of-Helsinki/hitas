import React, {useEffect, useRef, useState} from "react";

import {Button, IconPlus, IconSaveDisketteFill, Select} from "hds-react";
import {useImmer} from "use-immer";

import {useForm} from "react-hook-form";
import {GenericActionModal, QueryStateHandler, SaveButton} from "../../common/components";
import {FilterTextInputField} from "../../common/components/filters";
import {FormProviderForm, NumberInput, TextInput} from "../../common/components/forms";
import {IIndex} from "../../common/schemas";
import {useGetIndicesQuery, useSaveIndexMutation} from "../../common/services";
import {hdsToast} from "../../common/utils";

const indexOptions: {label: string; value: string}[] = [
    {label: "Markkinahintaindeksi 1983", value: "market-price-index"},
    {label: "Markkinahintaindeksi 2005", value: "market-price-index-2005-equal-100"},
    {label: "Rakennuskustannusindeksi 1980", value: "construction-price-index"},
    {label: "Rakennuskustannusindeksi 2005", value: "construction-price-index-2005-equal-100"},
    {label: "Rajaneliöhinta", value: "surface-area-price-ceiling"},
    {label: "Luovutushintaindeksi", value: "maximum-price-index"},
];

const IndexListItem = ({month, value, setFormData}: {month: string; value: number; setFormData}) => (
    <div
        className="results-list__item results-list__item--code"
        onClick={(e) => {
            e.preventDefault();
            setFormData({month: month, value: value});
        }}
    >
        <span className="month">{month}</span>
        <span className="value">{value}</span>
    </div>
);

const LoadedIndexResultsList = ({data, setFormData}) => {
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
                        setFormData={setFormData}
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
                    setFormData={({month, value}) => {
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

    const formRef = useRef<HTMLFormElement>(null);
    const formObject = useForm({
        defaultValues: formData,
        mode: "all",
    });

    const handleConfirmButtonClick = () => {
        formRef.current && formRef.current.dispatchEvent(new Event("submit", {cancelable: true, bubbles: true}));
    };

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
            formObject.reset();
            closeModal();
        } else {
            hdsToast.error("Indeksin tallennus epäonnistui");
        }
        // eslint-disable-next-line
    }, [isLoading, error, data]);

    return (
        <GenericActionModal
            title={`Tallenna ${indexType.label}`}
            modalIcon={<IconSaveDisketteFill />}
            isModalOpen={isModalOpen}
            closeModal={closeModal}
            confirmButton={
                <SaveButton
                    onClick={handleConfirmButtonClick}
                    isLoading={isLoading}
                />
            }
        >
            <FormProviderForm
                formObject={formObject}
                formRef={formRef}
                onSubmit={handleSaveIndex}
            >
                <TextInput
                    label="Kuukausi (VVVV-KK)"
                    name="month"
                    tooltipText="Esim 2022-12"
                    required
                />
                <NumberInput
                    label="Arvo"
                    allowDecimals={true}
                    name="value"
                    required
                />
            </FormProviderForm>
        </GenericActionModal>
    );
};

export default IndicesList;
