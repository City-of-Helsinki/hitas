import React, {useState} from "react";

import {Dialog, IconCrossCircle, IconSearch, Table, TextInput} from "hds-react";

import {QueryStateHandler} from "../index";
import {FormInputProps} from "./";

interface RelatedModelInputProps extends FormInputProps {
    fieldPath: string;
    requestedField?: string;
    queryFunction;
    setterFunction?;
    relatedModelSearchField: string;
    getRelatedModelLabel: (unknown) => string;
    placeholder?: string;
    children?: React.ReactNode;
}

const RelatedModelInput = ({
    name,
    id = name,
    label = "",
    required,
    children,
    requestedField = "id",
    queryFunction,
    setterFunction,
    relatedModelSearchField,
    getRelatedModelLabel,
    placeholder,
    formObject,
}: RelatedModelInputProps) => {
    // Form input
    const {
        register,
        formState: {errors},
    } = formObject;
    const formRelatedModel = register(name);
    const fieldName = formRelatedModel.name;

    // Flags & helper values
    const MIN_LENGTH = 2;
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [internalFilterValue, setInternalFilterValue] = useState("");
    const [displayedValue, setDisplayedValue] = useState(placeholder);
    const {data, error, isLoading} = queryFunction(
        (internalFilterValue.length >= MIN_LENGTH && {[relatedModelSearchField]: internalFilterValue}) || {},
        {skip: !isModalOpen}
    );
    const cols = [
        {key: "id", headerName: "Not rendered"},
        {
            key: "value",
            headerName: label || "Arvo",
            transform: getRelatedModelLabel,
        },
    ];
    // Events
    const setFieldValue = (value, displayValue = value) => {
        if (setterFunction) setterFunction(value);
        else formObject.setValue(fieldName, value, {shouldValidate: true});
        setDisplayedValue(displayValue);
    };
    const openModal = () => setIsModalOpen(true);
    const closeModal = () => setIsModalOpen(false);
    const clearFieldValue = () => {
        setFieldValue("");
    };
    // Handlers
    const handleSetSelectedRows = (rows) => {
        if (rows.length) {
            const objId = rows[0];
            const obj = data.contents[data.contents.findIndex((obj) => obj.id === objId)];
            setFieldValue(obj[requestedField], getRelatedModelLabel(obj));
            closeModal();
        }
    };

    const handleKeyDown = (e) => {
        // Make other key presses than Tab (and Shift+Tab) open the modal
        if (e.code !== ("Tab" || "Shift")) {
            e.preventDefault();
            openModal();
        }
    };

    return (
        <div className={`input-field input-field--related-model${required ? " input-field--required" : ""}`}>
            {children ? (
                children
            ) : (
                <TextInput
                    id={id || fieldName}
                    name={fieldName}
                    label={label}
                    required={required}
                    value={displayedValue || placeholder || (formObject.getValues(fieldName) ?? "")}
                    errorText={errors[fieldName]}
                    invalid={errors[fieldName]}
                    buttonIcon={!required && formObject.getValues(fieldName) ? <IconCrossCircle /> : <IconSearch />}
                    onButtonClick={!required && formObject.getValues(fieldName) ? clearFieldValue : openModal}
                    onKeyDown={(e) => handleKeyDown(e)}
                    onClick={openModal}
                />
            )}
            <Dialog
                id={`input-modal-${fieldName}`}
                aria-labelledby={label || fieldName}
                closeButtonLabelText="args.closeButtonLabelText"
                isOpen={isModalOpen}
                close={closeModal}
                theme={{
                    "--accent-line-color": "var(--color-black-80)",
                }}
            >
                <Dialog.Header
                    id={`input-modal-${fieldName}__title`}
                    title={`Valitse ${label}`}
                />
                <Dialog.Content>
                    <TextInput
                        id={`modal-search-${fieldName}`}
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
                            theme={{
                                "--header-background-color": "var(--color-black-80)",
                            }}
                        />
                        <span>
                            Näytetään {data?.page.size}/{data?.page.total_items} tulosta
                        </span>
                    </QueryStateHandler>
                </Dialog.Content>
            </Dialog>
        </div>
    );
};

export default RelatedModelInput;
