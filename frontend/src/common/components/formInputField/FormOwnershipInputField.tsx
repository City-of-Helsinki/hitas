import React, {useEffect, useState} from "react";

import {Button, Dialog, IconCrossCircle, IconPlus, IconSearch, Table, TextInput} from "hds-react";
import {useImmer} from "use-immer";

import {useCreateOwnerMutation} from "../../../app/services";
import {IOwner} from "../../models";
import {hitasToast, validateSocialSecurityNumber} from "../../utils";
import QueryStateHandler from "../QueryStateHandler";
import SaveButton from "../SaveButton";
import FormInputField, {CommonFormInputFieldProps} from "./FormInputField";

interface FormOwnershipInputFieldProps extends CommonFormInputFieldProps {
    fieldPath: string;
    requestedField?: string;
    queryFunction;
    relatedModelSearchField: string;
    getRelatedModelLabel: (unknown) => string;
    placeholder?: string;
}

const CreateNewOwner = ({
    formData,
    setFormData,
    error,
    isLoading,
    cancelAction,
    confirmAction,
    isInvalidSSNAllowed,
}) => {
    return (
        <>
            <Dialog.Content>
                {error ? (
                    <div>{`Virhe: ${error}`}</div>
                ) : (
                    <>
                        <FormInputField
                            inputType="text"
                            label="Nimi"
                            fieldPath="name"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                            required
                        />
                        <FormInputField
                            inputType="text"
                            label="Henkilö- tai Y-tunnus"
                            fieldPath="identifier"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                            validator={validateSocialSecurityNumber}
                            required
                        />
                        <FormInputField
                            inputType="text"
                            label="Sähköpostiosoite"
                            fieldPath="email"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                        <p
                            className="error-message"
                            style={{
                                display:
                                    !validateSocialSecurityNumber(formData.identifier) && isInvalidSSNAllowed
                                        ? ""
                                        : "none",
                            }}
                        >
                            "{formData.identifier}" ei ole oikea sosiaaliturvatunnus. Tallennetaanko silti?
                        </p>
                    </>
                )}
            </Dialog.Content>
            <Dialog.ActionButtons>
                <Button
                    onClick={cancelAction}
                    variant="secondary"
                    theme="black"
                >
                    Peruuta
                </Button>
                {!error && (
                    <SaveButton
                        isLoading={isLoading}
                        onClick={confirmAction}
                    />
                )}
            </Dialog.ActionButtons>
        </>
    );
};

export default function FormOwnershipInputField({
    label,
    value,
    requestedField = "id",
    fieldPath,
    setFieldValue,
    queryFunction,
    relatedModelSearchField,
    getRelatedModelLabel,
    placeholder,
    required,
    ...rest
}: FormOwnershipInputFieldProps): JSX.Element {
    const MIN_LENGTH = 2;
    const [isAddingNew, setIsAddingNew] = useState(false);
    const [isInvalidSSNAllowed, setIsInvalidSSNAllowed] = useState(false);
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [internalFilterValue, setInternalFilterValue] = useState("");
    const [displayedValue, setDisplayedValue] = useState(placeholder);
    const {data, error, isLoading} = queryFunction(
        (internalFilterValue.length >= MIN_LENGTH && {[relatedModelSearchField]: internalFilterValue}) || {},
        {skip: !isModalVisible}
    );
    const [formData, setFormData] = useImmer<IOwner>({
        name: "",
        identifier: "",
        email: "",
    });
    const [createOwner, {data: createData, error: createError, isLoading: isCreating}] = useCreateOwnerMutation();

    const openModal = () => setIsModalVisible(true);

    const closeModal = () => setIsModalVisible(false);

    const clearFieldValue = () => {
        setDisplayedValue("");
        setFieldValue("");
    };

    const handleSetSelectedRows = (rows) => {
        if (rows.length) {
            const objId = rows[0];
            const obj = data.contents[data.contents.findIndex((obj) => obj.id === objId)];
            setDisplayedValue(getRelatedModelLabel(obj));
            setFieldValue(obj[requestedField]);
            closeModal();
        }
    };

    const handleCreateOwnerButton = () => {
        if (validateSocialSecurityNumber(formData.identifier as string) || isInvalidSSNAllowed)
            createOwner({data: formData});
        else setIsInvalidSSNAllowed(true);
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

    useEffect(() => {
        setIsInvalidSSNAllowed(false);
    }, [formData.identifier, setIsInvalidSSNAllowed]);

    useEffect(() => {
        if (!isCreating && !createError && createData) {
            hitasToast("Omistaja lisätty onnistuneesti!");
            setDisplayedValue(createData.name);
            setFieldValue(createData.id);
            setIsAddingNew(false);
            closeModal();
        }
    }, [createData, createError, isCreating, setFieldValue]);

    return (
        <div className={`input-field input-field--related-model${required ? " input-field--required" : ""}`}>
            <TextInput
                label={label + (required ? " *" : "")}
                value={displayedValue || (displayedValue === undefined && placeholder) || value}
                onChange={() => null} // Disable typing
                buttonIcon={!required && value ? <IconCrossCircle /> : <IconSearch />}
                onButtonClick={!required && value ? clearFieldValue : openModal}
                onClick={openModal}
                {...rest}
            />
            <Dialog
                id={`modal-${fieldPath}`}
                closeButtonLabelText="args.closeButtonLabelText"
                aria-labelledby={label}
                isOpen={isModalVisible}
                close={() => setIsModalVisible(false)}
                boxShadow
                theme={dialogTheme}
            >
                <Dialog.Header
                    id={`modal-title-${fieldPath}`}
                    title={`${isAddingNew ? "Lisää uusi" : "Valitse"} omistaja`}
                    iconLeft={isAddingNew ? <IconPlus aria-hidden /> : <IconSearch aria-hidden />}
                />
                {isAddingNew ? (
                    <CreateNewOwner
                        formData={formData}
                        setFormData={setFormData}
                        error={createError}
                        isLoading={isCreating}
                        cancelAction={() => {
                            setIsInvalidSSNAllowed(false);
                            setIsAddingNew(false);
                        }}
                        confirmAction={handleCreateOwnerButton}
                        isInvalidSSNAllowed={isInvalidSSNAllowed}
                    />
                ) : (
                    <>
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
                            <Button
                                onClick={closeModal}
                                variant="secondary"
                                theme="black"
                            >
                                Sulje
                            </Button>
                            <Button
                                onClick={() => setIsAddingNew(true)}
                                theme="black"
                                iconLeft={<IconPlus />}
                            >
                                Lisää uusi
                            </Button>
                        </Dialog.ActionButtons>
                    </>
                )}
            </Dialog>
        </div>
    );
}
