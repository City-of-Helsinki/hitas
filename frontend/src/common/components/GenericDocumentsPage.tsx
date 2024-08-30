import {Button, Fieldset, IconArrowLeft, IconCrossCircle, IconDocument, IconPlus, StatusLabel} from "hds-react";
import {useCallback, useRef, useState} from "react";
import {SubmitHandler, useFieldArray, useForm, useFormContext} from "react-hook-form";
import {IApartmentDetails, IHousingCompanyDetails} from "../schemas";
import {FileInput, FormProviderForm, TextInput} from "./forms";
import {ConfirmDialogModal, FileDropZone, SaveButton} from "./index";

import {zodResolver} from "@hookform/resolvers/zod";
import {useNavigate} from "react-router-dom";
import {v4 as uuidv4} from "uuid";
import {
    useDeleteApartmentDocumentMutation,
    useDeleteHousingCompanyDocumentMutation,
    useSaveApartmentDocumentMutation,
    useSaveHousingCompanyDocumentMutation,
} from "../services";
import {formatDate, hdsToast} from "../utils";
import {
    ApartmentDocumentsFormSchema,
    HousingCompanyDocumentsFormSchema,
    IApartmentDocumentsForm,
    IHousingCompanyDocumentsForm,
} from "../schemas/document";

const emptyDocument = {
    saved: false,
    display_name: "",
    file_object: null,
};

const DocumentAddEmptyLineButton = ({append}) => {
    return (
        <Button
            onClick={() =>
                append({
                    key: uuidv4(),
                    ...emptyDocument,
                })
            }
            iconLeft={<IconPlus />}
            theme="black"
        >
            Lisää dokumentti
        </Button>
    );
};

const DocumentRemoveLineButton = ({name, index, remove}) => {
    const formObject = useFormContext();
    const [isConfirmVisible, setIsConfirmVisible] = useState(false);
    const document = formObject.getValues(`${name}.${index}`);

    const handleRemoveButtonPress = () => {
        const document = formObject.getValues(`${name}.${index}`);

        // If all fields are empty, remove without confirmation
        if (!document.display_name && !document.file_object && !document.id) {
            remove(index);
            return;
        } else {
            setIsConfirmVisible(true);
        }
    };

    return (
        <div className="icon--remove">
            <IconCrossCircle
                size="m"
                onClick={handleRemoveButtonPress}
            />

            <ConfirmDialogModal
                modalText={`Haluatko varmasti poistaa dokumentin ${document.display_name}?`}
                buttonText="Poista"
                successText="Parannus poistettu"
                isVisible={isConfirmVisible}
                setIsVisible={setIsConfirmVisible}
                confirmAction={() => {
                    if (document.id) {
                        const removedDocumentIds = formObject.getValues("removedDocumentIds") ?? [];
                        formObject.setValue("removedDocumentIds", [...removedDocumentIds, document.id]);
                        hdsToast.info(
                            `Dokumentti ${document.display_name} merkattu poistettavaksi.\nMuistathan vielä tallentaa.`,
                            {
                                duration: 10000,
                            }
                        );
                    }
                    remove(index);
                    setIsConfirmVisible(false);
                }}
                cancelAction={() => setIsConfirmVisible(false)}
            />
        </div>
    );
};

const DocumentsListItems = ({name, remove}) => {
    const formObject = useFormContext();
    const documents = formObject.watch(name);
    const documentListItemRef = useRef(null);
    return (
        <>
            {documents.map((document, index) => (
                <li
                    className="documents-list-item"
                    key={`document-item-${document.id ?? document.key}`}
                    ref={documentListItemRef}
                >
                    <TextInput
                        label="Nimi"
                        name={`${name}.${index}.display_name`}
                        required
                    />
                    <div className="document-list-item-file-row">
                        <FileInput
                            label="Tiedosto"
                            buttonLabel={
                                document.file_link || document.file_object ? "Vaihda tiedosto" : "Valitse tiedosto"
                            }
                            name={`${name}.${index}.file_object`}
                            onChange={(filesArray) => {
                                // File is a required field but the HDS file input clears the native input after selection so the form is always invalid.
                                // This is a hack to make sure the native input has a file if the user has selected one so that the form can be submitted.
                                const documentListItem = documentListItemRef.current as HTMLElement | null;
                                const fileInput = documentListItem?.querySelector(
                                    'input[type="file"]'
                                ) as HTMLInputElement | null;
                                if (fileInput) {
                                    const datatransfer = new DataTransfer();
                                    datatransfer.items.add(filesArray[0]);
                                    setTimeout(() => (fileInput.files = datatransfer.files), 10);
                                }
                                // Explicitly mark as dirty, since react-hook-form does not support File objects for dirty checking.
                                formObject.setValue(`${name}.${index}.file_object`, filesArray[0], {shouldDirty: true});
                            }}
                            required={!document.file_link}
                            defaultValue={document.file_object ? [document.file_object] : []}
                        />
                        {!document.file_object && document.file_link && (
                            <a
                                href={document.file_link}
                                className="document-item-file-link"
                                target="_blank"
                                rel="noreferrer"
                            >
                                <IconDocument aria-hidden />
                                <div>
                                    {document.display_name}{" "}
                                    {document.file_type_display && `(${document.file_type_display})`}{" "}
                                </div>
                            </a>
                        )}
                    </div>
                    {(document.created_at || document.modified_at) && (
                        <div className="documents-list-item-metadata">
                            {document.created_at && (
                                <StatusLabel>Lisätty: {formatDate(document.created_at.split("T")[0])}</StatusLabel>
                            )}
                            {document.modified_at && (
                                <StatusLabel>
                                    Tallennettu viimeksi: {formatDate(document.modified_at.split("T")[0])}
                                </StatusLabel>
                            )}
                        </div>
                    )}
                    <DocumentRemoveLineButton
                        name={name}
                        index={index}
                        remove={remove}
                    />
                </li>
            ))}
        </>
    );
};

export const DocumentFieldSet = ({fieldsetHeader, name}) => {
    const formObject = useFormContext();
    const {fields, append, remove} = useFieldArray({
        name: name,
        control: formObject.control,
    });
    formObject.register(name);

    return (
        <Fieldset heading={fieldsetHeader}>
            <ul className="documents-list">
                {fields.length ? (
                    <DocumentsListItems
                        name={name}
                        remove={remove}
                    />
                ) : (
                    <div>Ei dokumentteja</div>
                )}
                <li className="row row--buttons">
                    <DocumentAddEmptyLineButton append={append} />
                </li>
            </ul>
        </Fieldset>
    );
};

type IGenericDocumentsPage = {
    housingCompany: IHousingCompanyDetails;
    apartment?: IApartmentDetails;
};

const GenericDocumentsPage = ({housingCompany, apartment}: IGenericDocumentsPage) => {
    const navigate = useNavigate();
    const returnUrl =
        apartment === undefined
            ? `/housing-companies/${housingCompany.id}`
            : `/housing-companies/${housingCompany.id}/apartments/${apartment.id}`;
    const [isLeaveConfirmVisible, setIsLeaveConfirmVisible] = useState(false);

    // Select either apartment or housing company
    let formSchema;
    let saveDocumentHook;
    let deleteDocumentHook;
    let documentMutationArguments;
    let documents;

    if (apartment !== undefined) {
        formSchema = ApartmentDocumentsFormSchema;
        saveDocumentHook = useSaveApartmentDocumentMutation;
        deleteDocumentHook = useDeleteApartmentDocumentMutation;
        documentMutationArguments = {
            housingCompanyId: housingCompany.id,
            apartmentId: apartment.id,
        };
        documents = apartment.documents;
    } else {
        formSchema = HousingCompanyDocumentsFormSchema;
        saveDocumentHook = useSaveHousingCompanyDocumentMutation;
        deleteDocumentHook = useDeleteHousingCompanyDocumentMutation;
        documentMutationArguments = {
            housingCompanyId: housingCompany.id,
        };
        documents = housingCompany.documents;
    }

    documents = documents.toSorted((a, b) => a.display_name.localeCompare(b.display_name));

    // Form
    const initialFormData = {
        documents: documents,
        removedDocumentIds: [],
    };

    const formObject = useForm({
        resolver: zodResolver(formSchema),
        defaultValues: initialFormData,
        mode: "all",
    });

    const {
        fields: documentFields,
        append: appendDocument,
        remove: removeDocument,
    } = useFieldArray({
        name: "documents",
        control: formObject.control,
    });
    formObject.register("documents");

    // API Handling
    const [saveDocument, {isSaveLoading}] = saveDocumentHook();
    const [deleteDocument, {isDeleteLoading}] = deleteDocumentHook();

    const onSubmit: SubmitHandler<IApartmentDocumentsForm | IHousingCompanyDocumentsForm> = (formData) => {
        const documentRequests: Promise<void>[] = [];
        for (const document of formData.documents) {
            const documentFormData = new FormData();
            documentFormData.append("display_name", document.display_name);
            if (document.file_object) {
                documentFormData.append("file_content", document.file_object);
            }
            const request = saveDocument({
                ...documentMutationArguments,
                id: document.id,
                data: documentFormData,
            }).unwrap();
            documentRequests.push(request);
        }
        for (const removedDocumentId of formData.removedDocumentIds) {
            const request = deleteDocument({
                ...documentMutationArguments,
                documentId: removedDocumentId,
            }).unwrap();
            documentRequests.push(request);
        }
        Promise.all(documentRequests)
            .then(() => {
                hdsToast.success("Dokumentit tallennettu onnistuneesti!");
                setTimeout(() => navigate(returnUrl), 1000);
            })
            .catch(() => hdsToast.error("Virhe tallentaessa dokumentteja!"));
    };

    const onBackButtonClick = useCallback(() => {
        if (formObject.formState.isDirty) {
            setIsLeaveConfirmVisible(true);
        } else {
            navigate(returnUrl);
        }
    }, [formObject.formState.isDirty]);

    return (
        <>
            <FormProviderForm
                formObject={formObject}
                onSubmit={onSubmit}
            >
                {initialFormData.documents.length >= 3 ? (
                    <div
                        className="row row--buttons"
                        style={{marginTop: "0"}}
                    >
                        <Button
                            iconLeft={<IconArrowLeft />}
                            theme="black"
                            variant="secondary"
                            className="back-button"
                            onClick={onBackButtonClick}
                        >
                            Takaisin
                        </Button>
                        <SaveButton
                            type="submit"
                            isLoading={isSaveLoading || isDeleteLoading}
                        />
                    </div>
                ) : (
                    ""
                )}
                <div className="field-sets">
                    <Fieldset heading={apartment === undefined ? "Taloyhtiön dokumentit" : "Asunnon dokumentit"}>
                        <ul className="documents-list">
                            {documentFields.length ? (
                                <DocumentsListItems
                                    name="documents"
                                    remove={removeDocument}
                                />
                            ) : (
                                <div>Ei dokumentteja</div>
                            )}
                            <li className="row row--buttons">
                                <DocumentAddEmptyLineButton append={appendDocument} />
                            </li>
                        </ul>
                    </Fieldset>
                    <FileDropZone
                        onFileDrop={(files) => {
                            for (const file of files) {
                                appendDocument({
                                    ...emptyDocument,
                                    key: uuidv4(),
                                    file_object: file,
                                });
                            }
                        }}
                        helpText="Pudota tiedostot tähän lisätäksesi ne dokumenteiksi."
                    />
                </div>
                <div className="row row--buttons">
                    <Button
                        iconLeft={<IconArrowLeft />}
                        theme="black"
                        variant="secondary"
                        className="back-button"
                        onClick={onBackButtonClick}
                    >
                        Takaisin
                    </Button>
                    <SaveButton
                        type="submit"
                        isLoading={isSaveLoading || isDeleteLoading}
                    />
                </div>
            </FormProviderForm>

            <ConfirmDialogModal
                className="document-create-confirm-leave-modal"
                modalText="Lomakkeella on tallentamattomia muutoksia. Haluatko siirtyä pois?"
                buttonText="Poistu lomakkeelta tallentamatta"
                cancelButtonText="Palaa lomakkeelle"
                isVisible={isLeaveConfirmVisible}
                setIsVisible={setIsLeaveConfirmVisible}
                confirmAction={() => navigate(returnUrl)}
                cancelAction={() => setIsLeaveConfirmVisible(false)}
            />
        </>
    );
};

export default GenericDocumentsPage;
