import React, {useState} from "react";

import {Button, Dialog, IconCrossCircle, IconSearch, LoadingSpinner, Table, TextInput} from "hds-react";

import {CommonFormInputFieldProps} from "./FormInputField";

interface FormRelatedModelInputFieldProps extends CommonFormInputFieldProps {
    fieldPath: string;
    queryFunction;
    relatedModelSearchField: string;
    getRelatedModelLabel: (unknown) => string;
}

export default function FormRelatedModelInputField({
    label,
    value,
    fieldPath,
    setFieldValue,
    queryFunction,
    relatedModelSearchField,
    getRelatedModelLabel,
    ...rest
}: FormRelatedModelInputFieldProps): JSX.Element {
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [internalFilterValue, setInternalFilterValue] = useState("");
    const [displayedValue, setDisplayedValue] = useState("");

    const {data, isLoading} = queryFunction({[relatedModelSearchField]: internalFilterValue}, {skip: !isModalVisible});

    const openModal = () => setIsModalVisible(true);
    const closeModal = () => setIsModalVisible(false);

    const handleSetSelectedRows = (rows) => {
        if (rows.length) {
            const objId = rows[0];
            const obj = data.contents[data.contents.findIndex((obj) => obj.id === objId)];
            setDisplayedValue(getRelatedModelLabel(obj));
            setFieldValue(objId);
            closeModal();
        }
    };

    const cols = [
        {key: "id", headerName: "Not rendered"},
        {
            key: "age",
            headerName: label,
            transform: getRelatedModelLabel,
        },
    ];

    return (
        <div>
            <TextInput
                label={label}
                value={displayedValue || value}
                onChange={() => null} // Disable typing
                buttonIcon={<IconSearch />}
                onButtonClick={openModal}
                onClick={openModal}
                {...rest}
            />
            <Dialog
                id={`modal-${fieldPath}`}
                closeButtonLabelText={"args.closeButtonLabelText"}
                aria-labelledby={label}
                isOpen={isModalVisible}
                close={() => setIsModalVisible(false)}
                boxShadow={true}
            >
                <Dialog.Header
                    id={`modal-title-${fieldPath}`}
                    title={`Valitse ${label}`}
                    iconLeft={<IconSearch aria-hidden="true" />}
                />
                <Dialog.Content>
                    <TextInput
                        id={`modal-search-${fieldPath}`}
                        label="Hae"
                        value={internalFilterValue}
                        onChange={(e) => setInternalFilterValue(e.target.value)}
                        buttonIcon={internalFilterValue ? <IconCrossCircle /> : null}
                        onButtonClick={() => setInternalFilterValue("")}
                    />
                    <br />
                    {isLoading ? (
                        <LoadingSpinner />
                    ) : (
                        // TODO: Remove 'Select all' and 'Clear selected' buttons
                        <>
                            <Table
                                cols={cols}
                                rows={data?.contents}
                                indexKey="id"
                                renderIndexCol={false}
                                checkboxSelection
                                selectedRows={[]}
                                setSelectedRows={handleSetSelectedRows}
                                zebra
                            />
                            <span>
                                Näytetään {data?.page.size}/{data?.page.total_items} tulosta
                            </span>
                        </>
                    )}
                </Dialog.Content>
                <Dialog.ActionButtons>
                    <Button
                        onClick={closeModal}
                        disabled
                    >
                        Lisää uusi
                    </Button>
                    <Button
                        onClick={closeModal}
                        variant="secondary"
                    >
                        Sulje
                    </Button>
                </Dialog.ActionButtons>
            </Dialog>
        </div>
    );
}
