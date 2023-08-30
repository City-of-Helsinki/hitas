import React, {useState} from "react";

import {Button, Dialog, IconCrossCircle, IconPlus, IconSearch, Table, TextInput} from "hds-react";

import {useFormContext} from "react-hook-form";
import {dotted} from "../../utils";
import {QueryStateHandler} from "../index";

type IRelatedModelMutateComponent = React.FC<{
    name: string;
    cancelButtonAction: () => void;
    closeModalAction: () => void;
    saveSuccessCallback?: (unknown) => void;
}>;

const RelatedModelTextInput = ({label, required, disabled, name, transform, openModal}) => {
    const formObject = useFormContext();

    const fieldValue = formObject.getValues(name);
    const isFieldClearable = !required && fieldValue;
    const errors = formObject.formState.errors;
    const fieldError = dotted(errors, name);

    const handleKeyDown = (e) => {
        // Make other key presses than Tab (and Shift+Tab) open the modal
        if (e.code !== "Tab" && !e.shiftKey) {
            e.preventDefault();
            openModal();
        }
    };

    const clearFieldValue = () => {
        formObject.watch(name);
        formObject.setValue(name, null);
    };

    return (
        <TextInput
            id={name}
            label={label}
            name={name}
            value={fieldValue ? transform(fieldValue) : ""}
            onClick={openModal}
            onKeyDown={(e) => handleKeyDown(e)}
            buttonIcon={isFieldClearable ? <IconCrossCircle /> : <IconSearch />}
            onButtonClick={isFieldClearable ? clearFieldValue : openModal}
            errorText={fieldError ? (fieldError as {message: string}).message : ""}
            invalid={!!fieldError}
            required={required}
            disabled={disabled}
        />
    );
};

interface RelatedModelModalProps {
    label: string;
    queryFunction;
    relatedModelSearchField: string;
    name: string;
    formatFormObjectValue: (unknown) => string;
    transform?: (unknown) => string;
    isModalOpen: boolean;
    closeModal: () => void;
    // If component is passed, creating new objects is enabled
    RelatedModelMutateComponent?: IRelatedModelMutateComponent;
}

const RelatedModelModal = ({
    label,
    name,
    queryFunction,
    relatedModelSearchField,
    formatFormObjectValue,
    transform,
    isModalOpen,
    closeModal,
    RelatedModelMutateComponent,
}: RelatedModelModalProps) => {
    const formObject = useFormContext();

    const MIN_LENGTH = 2; // Minimum length before applying filter
    const [internalFilterValue, setInternalFilterValue] = useState("");
    const [isRelatedModelMutateVisible, setIsRelatedModelMutateVisible] = useState(false);

    const {data, error, isLoading} = queryFunction(
        (internalFilterValue.length >= MIN_LENGTH && {[relatedModelSearchField]: internalFilterValue}) || {},
        {skip: !isModalOpen}
    );

    const cols = [
        {key: "id", headerName: "Not rendered"},
        {
            key: "value",
            headerName: label,
            transform: transform ?? formatFormObjectValue,
        },
    ];

    const setFieldValue = (value) => {
        formObject.setValue(name, value, {shouldValidate: true});
    };

    // Triggered when a table checkbox is clicked
    const handleSetSelectedRows = (rows) => {
        if (rows.length === 1) {
            const objId = rows[0];
            const obj = data.contents[data.contents.findIndex((obj) => obj.id === objId)];
            if (transform !== undefined) {
                setFieldValue(transform(obj));
            } else {
                setFieldValue(obj);
            }

            closeModal();
        }
    };

    return (
        <Dialog
            id={`input-modal-${name}`}
            aria-labelledby={label || name}
            closeButtonLabelText="args.closeButtonLabelText"
            isOpen={isModalOpen}
            close={() => {
                closeModal();
                setIsRelatedModelMutateVisible(false);
            }}
            theme={{
                "--accent-line-color": "var(--color-black-80)",
            }}
        >
            <Dialog.Header
                id={`input-modal-${name}__title`}
                title={isRelatedModelMutateVisible ? `Luo uusi ${label}` : `Valitse ${label}`}
            />
            <Dialog.Content>
                <div className="input-field--related-model--modal--content">
                    {isRelatedModelMutateVisible && RelatedModelMutateComponent ? (
                        <RelatedModelMutateComponent
                            name={name}
                            cancelButtonAction={() => setIsRelatedModelMutateVisible(false)}
                            closeModalAction={() => closeModal()}
                            saveSuccessCallback={setFieldValue}
                        />
                    ) : (
                        <>
                            <TextInput
                                id={`modal-search-${name}`}
                                className="text-input-search"
                                label="Hae"
                                value={internalFilterValue}
                                onChange={(e) => setInternalFilterValue(e.target.value)}
                                onButtonClick={() => setInternalFilterValue("")}
                                buttonIcon={internalFilterValue ? <IconCrossCircle /> : null}
                            />
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
                                <span className="results-count">
                                    Näytetään {data?.page.size}/{data?.page.total_items} tulosta.
                                </span>
                            </QueryStateHandler>
                            {RelatedModelMutateComponent ? (
                                <Button
                                    theme="black"
                                    iconLeft={<IconPlus />}
                                    onClick={() => setIsRelatedModelMutateVisible(true)}
                                >
                                    Luo uusi
                                </Button>
                            ) : null}
                        </>
                    )}
                </div>
            </Dialog.Content>
        </Dialog>
    );
};

interface RelatedModelInputProps {
    label: string;
    // Place in form where the whole object is stored and set
    name: string;

    queryFunction;
    relatedModelSearchField: string;

    // Format form value to a string. Displayed on the input field (and modal list)
    transform: (unknown) => string;
    // Used when the form expects a string, not an object.
    // Format the relatedModel object before setting it to the form. If defined, used in the modal list instead of transform.
    formatObjectForForm?: (unknown) => string;

    invalid?: boolean;
    errorText?: string;
    tooltipText?: string;

    RelatedModelMutateComponent?: IRelatedModelMutateComponent;
    required?: boolean;
    disabled?: boolean;
}

const RelatedModelInput = ({
    label,
    name,

    queryFunction,
    relatedModelSearchField,

    transform,
    formatObjectForForm,

    RelatedModelMutateComponent,

    required,
    disabled,
}: RelatedModelInputProps) => {
    const formObject = useFormContext();
    formObject.register(name);

    const [isModalOpen, setIsModalOpen] = useState(false);
    const openModal = () => setIsModalOpen(true);
    const closeModal = () => setIsModalOpen(false);

    return (
        <div className={`input-field input-field--related-model${required ? " input-field--required" : ""}`}>
            <RelatedModelTextInput
                label={label}
                name={name}
                transform={transform}
                openModal={openModal}
                required={required}
                disabled={disabled}
            />
            <RelatedModelModal
                label={label}
                name={name}
                queryFunction={queryFunction}
                relatedModelSearchField={relatedModelSearchField}
                formatFormObjectValue={transform}
                transform={formatObjectForForm}
                isModalOpen={isModalOpen}
                closeModal={closeModal}
                RelatedModelMutateComponent={RelatedModelMutateComponent}
            />
        </div>
    );
};

export default RelatedModelInput;
