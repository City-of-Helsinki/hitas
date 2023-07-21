import React, {useRef, useState} from "react";

import {Button, IconPlus, IconSaveDisketteFill, Select} from "hds-react";

import {zodResolver} from "@hookform/resolvers/zod";
import {useForm} from "react-hook-form";
import {GenericActionModal, QueryStateHandler} from "../../common/components";
import {FilterTextInputField} from "../../common/components/filters";
import {FormProviderForm, NumberInput, SaveFormButton, TextInput} from "../../common/components/forms";
import {IIndex, IndexSchema} from "../../common/schemas";
import {useGetIndicesQuery, useSaveIndexMutation} from "../../common/services";
import {hdsToast, setAPIErrorsForFormFields, today} from "../../common/utils";

const indexOptions: {label: string; value: string}[] = [
    {label: "Markkinahintaindeksi 1983", value: "market-price-index"},
    {label: "Markkinahintaindeksi 2005", value: "market-price-index-2005-equal-100"},
    {label: "Rakennuskustannusindeksi 1980", value: "construction-price-index"},
    {label: "Rakennuskustannusindeksi 2005", value: "construction-price-index-2005-equal-100"},
    {label: "Rajaneliöhinta", value: "surface-area-price-ceiling"},
    {label: "Luovutushintaindeksi", value: "maximum-price-index"},
];

const EditIndexModal = ({
    indexType,
    index,
    isModalOpen,
    closeModal,
}: {
    indexType: {label: string; value: string};
    index?: IIndex;
    isModalOpen: boolean;
    closeModal: () => void;
}) => {
    const [saveIndex, {isLoading}] = useSaveIndexMutation();

    const formRef = useRef<HTMLFormElement>(null);
    const formObject = useForm({
        defaultValues: index ?? {month: today().split("-").slice(0, 2).join("-"), value: undefined},
        mode: "all",
        resolver: zodResolver(IndexSchema),
    });

    const handleSaveIndex = (data) => {
        saveIndex({
            index: indexType.value,
            month: data.month,
            data: data,
        })
            .unwrap()
            .then(() => {
                hdsToast.success("Indeksi tallennettu onnistuneesti");
                formObject.reset();
                closeModal();
            })
            .catch((error) => {
                hdsToast.error("Indeksin tallennus epäonnistui");
                setAPIErrorsForFormFields(formObject, error);
            });
    };

    return (
        <GenericActionModal
            title={`Tallenna ${indexType.label}`}
            modalIcon={<IconSaveDisketteFill />}
            isModalOpen={isModalOpen}
            closeModal={closeModal}
            confirmButton={
                <SaveFormButton
                    formRef={formRef}
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
                />
            </FormProviderForm>
        </GenericActionModal>
    );
};

const IndexListItem = ({indexType, index}: {indexType: {label: string; value: string}; index: IIndex}) => {
    const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
    const closeModal = () => setIsModalOpen(false);

    return (
        <>
            <div
                className="results-list__item results-list__item--code"
                onClick={() => setIsModalOpen(true)}
            >
                <span className="month">{index.month}</span>
                <span className="value">{index.value}</span>
            </div>
            <EditIndexModal
                indexType={indexType}
                index={index}
                isModalOpen={isModalOpen}
                closeModal={closeModal}
            />
        </>
    );
};

const IndexResultTable = ({indexType, filterParams}) => {
    const {data, currentData, error, isFetching} = useGetIndicesQuery({
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
                isLoading={isFetching}
            >
                <div className="list-headers">
                    <div className="list-header month">Kuukausi</div>
                    <div className="list-header value">Arvo</div>
                </div>
                <ul className="results-list">
                    {currentData?.contents.map((index: IIndex) => (
                        <IndexListItem
                            key={index.month}
                            indexType={indexType}
                            index={index}
                        />
                    ))}
                </ul>
            </QueryStateHandler>
        </div>
    );
};

const IndicesTab = (): React.JSX.Element => {
    const [filterParams, setFilterParams] = useState({});
    const [currentIndexType, setCurrentIndexType] = useState(indexOptions[0]);

    const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
    const closeModal = () => setIsModalOpen(false);

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

            <IndexResultTable
                indexType={currentIndexType}
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
                index={undefined}
                isModalOpen={isModalOpen}
                closeModal={closeModal}
            />
        </div>
    );
};

export default IndicesTab;
