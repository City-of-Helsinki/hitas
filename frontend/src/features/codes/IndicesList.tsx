import {useEffect, useState} from "react";

import {Button, Dialog, IconPlus, Select} from "hds-react";
import {useImmer} from "use-immer";

import {useGetIndicesQuery, useSaveIndexMutation} from "../../app/services";
import {FilterTextInputField, FormInputField, QueryStateHandler, SaveButton} from "../../common/components";
import {IIndex} from "../../common/schemas";
import {hitasToast} from "../../common/utils";

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

const IndicesList = (): JSX.Element => {
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
            index: indexType.value,
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
                title={`Tallenna ${indexType.label}`}
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
