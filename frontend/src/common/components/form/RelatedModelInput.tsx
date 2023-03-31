import {useState} from "react";

import {Dialog, IconCrossCircle, IconSearch, Table, TextInput} from "hds-react";

import {QueryStateHandler} from "../index";

const RelatedModelTextInput = ({
    label,
    required,
    disabled,
    formObject,
    formObjectFieldPath,
    formatFormObjectValue,
    openModal,
}) => {
    const fieldValue = formObject.getValues(formObjectFieldPath);
    const isFieldClearable = !required && fieldValue;
    const errors = formObject.formState.errors;

    const handleKeyDown = (e) => {
        // Make other key presses than Tab (and Shift+Tab) open the modal
        if (e.code !== "Tab" && !e.shiftKey) {
            e.preventDefault();
            openModal();
        }
    };

    const clearFieldValue = () => {
        formObject.setValue(formObjectFieldPath, "");
    };

    return (
        <TextInput
            id={formObjectFieldPath}
            name={formObjectFieldPath}
            label={label}
            required={required}
            disabled={disabled}
            value={formatFormObjectValue(fieldValue)}
            onClick={openModal}
            onKeyDown={(e) => handleKeyDown(e)}
            buttonIcon={isFieldClearable ? <IconCrossCircle /> : <IconSearch />}
            onButtonClick={isFieldClearable ? clearFieldValue : openModal}
            errorText={errors[formObjectFieldPath]}
            invalid={!!errors[formObjectFieldPath]}
        />
    );
};

const RelatedModelModal = ({
    label,
    queryFunction,
    relatedModelSearchField,
    formObject,
    formObjectFieldPath,
    formatFormObjectValue,
    isModalOpen,
    closeModal,
}) => {
    const MIN_LENGTH = 2; // Minimum length before applying filter
    const [internalFilterValue, setInternalFilterValue] = useState("");

    const {data, error, isLoading} = queryFunction(
        (internalFilterValue.length >= MIN_LENGTH && {[relatedModelSearchField]: internalFilterValue}) || {},
        {skip: !isModalOpen}
    );

    const cols = [
        {key: "id", headerName: "Not rendered"},
        {
            key: "value",
            headerName: label || "Arvo",
            transform: formatFormObjectValue,
        },
    ];

    const setFieldValue = (value) => {
        formObject.setValue(formObjectFieldPath, value, {shouldValidate: true});
    };

    // Triggered when a table checkbox is clicked
    const handleSetSelectedRows = (rows) => {
        if (rows.length === 1) {
            const objId = rows[0];
            const obj = data.contents[data.contents.findIndex((obj) => obj.id === objId)];
            setFieldValue(obj);
            closeModal();
        }
    };

    return (
        <Dialog
            id={`input-modal-${formObjectFieldPath}`}
            aria-labelledby={label || formObjectFieldPath}
            closeButtonLabelText="args.closeButtonLabelText"
            isOpen={isModalOpen}
            close={closeModal}
            theme={{
                "--accent-line-color": "var(--color-black-80)",
            }}
        >
            <Dialog.Header
                id={`input-modal-${formObjectFieldPath}__title`}
                title={`Valitse ${label}`}
            />
            <Dialog.Content>
                <TextInput
                    id={`modal-search-${formObjectFieldPath}`}
                    label="Hae"
                    value={internalFilterValue}
                    onChange={(e) => setInternalFilterValue(e.target.value)}
                    onButtonClick={() => setInternalFilterValue("")}
                    buttonIcon={internalFilterValue ? <IconCrossCircle /> : null}
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
                        Näytetään {data?.page.size}/{data?.page.total_items} tulosta.
                    </span>
                </QueryStateHandler>
            </Dialog.Content>
        </Dialog>
    );
};

interface RelatedModelInputProps {
    label?: string;
    required?: boolean;
    disabled?: boolean;

    queryFunction;
    relatedModelSearchField: string;

    formObject?;
    formObjectFieldPath: string;
    formatFormObjectValue: (unknown) => string;

    invalid?: boolean;
    errorText?: string;
    tooltipText?: string;
}

const RelatedModelInput = ({
    label,
    required,
    disabled,

    queryFunction,
    relatedModelSearchField,

    formObject,
    formObjectFieldPath,
    formatFormObjectValue,
}: RelatedModelInputProps) => {
    formObject.register(formObjectFieldPath);

    const [isModalOpen, setIsModalOpen] = useState(false);
    const openModal = () => setIsModalOpen(true);
    const closeModal = () => setIsModalOpen(false);

    return (
        <div className={`input-field input-field--related-model${required ? " input-field--required" : ""}`}>
            <RelatedModelTextInput
                label={label}
                required={required}
                disabled={disabled}
                formObject={formObject}
                formObjectFieldPath={formObjectFieldPath}
                formatFormObjectValue={formatFormObjectValue}
                openModal={openModal}
            />
            <RelatedModelModal
                label={label}
                formObject={formObject}
                formObjectFieldPath={formObjectFieldPath}
                queryFunction={queryFunction}
                relatedModelSearchField={relatedModelSearchField}
                formatFormObjectValue={formatFormObjectValue}
                isModalOpen={isModalOpen}
                closeModal={closeModal}
            />
        </div>
    );
};

export default RelatedModelInput;
