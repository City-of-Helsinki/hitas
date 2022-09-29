import React, {useState} from "react";

import {Button, Dialog, IconCrossCircle, IconSearch, Table, TextInput} from "hds-react";

import QueryStateHandler from "../QueryStateHandler";
import {CommonFormInputFieldProps} from "./FormInputField";

interface FormRelatedModelInputFieldProps extends CommonFormInputFieldProps {
    fieldPath: string;
    requestedField?: string;
    queryFunction;
    relatedModelSearchField: string;
    getRelatedModelLabel: (unknown) => string;
    placeholder?: string;
}

export default function FormRelatedModelInputField({
    label,
    value,
    requestedField = "id",
    fieldPath,
    setFieldValue,
    queryFunction,
    relatedModelSearchField,
    getRelatedModelLabel,
    placeholder,
    ...rest
}: FormRelatedModelInputFieldProps): JSX.Element {
    const MIN_LENGTH = 2;
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [internalFilterValue, setInternalFilterValue] = useState("");
    const [displayedValue, setDisplayedValue] = useState(placeholder);

    const {data, error, isLoading} = queryFunction(
        (internalFilterValue.length >= MIN_LENGTH && {[relatedModelSearchField]: internalFilterValue}) || {},
        {skip: !isModalVisible}
    );

    const openModal = () => setIsModalVisible(true);
    const closeModal = () => setIsModalVisible(false);

    const handleSetSelectedRows = (rows) => {
        if (rows.length) {
            const objId = rows[0];
            const obj = data.contents[data.contents.findIndex((obj) => obj.id === objId)];
            setDisplayedValue(getRelatedModelLabel(obj));
            setFieldValue(obj[requestedField]);
            closeModal();
        }
    };

    const dialogTheme = {
        "--accent-line-color": "var(--color-black-80)",
    };

    const tableTheme = {
        "--header-background-color": "var(--color-black-80)",
    };

    const cols = [
        {key: "id", headerName: "Not rendered"},
        {
            key: "value",
            headerName: label,
            transform: getRelatedModelLabel,
        },
    ];

    return (
        <div>
            <TextInput
                label={label}
                value={displayedValue || (!displayedValue && placeholder) || value}
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
                theme={dialogTheme}
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
                    <QueryStateHandler
                        data={data}
                        error={error}
                        isLoading={isLoading}
                    >
                        <Table
                            cols={cols}
                            rows={data?.contents}
                            indexKey="id"
                            renderIndexCol={false}
                            checkboxSelection
                            selectedRows={[]}
                            setSelectedRows={handleSetSelectedRows}
                            zebra
                            theme={tableTheme}
                        />
                        <span>
                            Näytetään {data?.page.size}/{data?.page.total_items} tulosta
                        </span>
                    </QueryStateHandler>
                </Dialog.Content>
                <Dialog.ActionButtons>
                    {/* TODO: Adding to the related data is handled by the Django dashboard for now. This feature is to be shown here later
                     <Button
                     onClick={closeModal}
                     disabled
                     theme={"black"}
                     >
                     Lisää uusi
                     </Button>
                     */}
                    <Button
                        onClick={closeModal}
                        variant="secondary"
                        theme={"black"}
                    >
                        Sulje
                    </Button>
                </Dialog.ActionButtons>
            </Dialog>
        </div>
    );
}
