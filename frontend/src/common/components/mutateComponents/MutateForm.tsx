import {zodResolver} from "@hookform/resolvers/zod";
import {Button, ButtonPresetTheme, IconArrowLeft} from "hds-react";
import {useEffect, useState} from "react";
import {useForm} from "react-hook-form";
import {hdsToast} from "../../utils";
import {FormProviderForm, TextInput} from "../forms";
import SaveButton from "../SaveButton";
import DeleteButton from "../DeleteButton";
import ConfirmDialogModal from "../ConfirmDialogModal";

export interface IMutateFormProps<TFormFieldsWithTitles extends object> {
    formObjectSchema;
    useSaveMutation;
    deleteProps?: {
        useDeleteMutation;
        modalText: string | ((object) => string);
        successText: string;
        successToastText: string;
        errorToastText: string;
    };
    successMessage: string;
    errorMessage: string;
    notModifiedMessage: string;
    formFieldsWithTitles: TFormFieldsWithTitles;
    requiredFields: string[];
}

export type IMutateForm<TDefaultObject extends object, TFormFieldsWithTitles extends object> = {
    defaultObject?: TDefaultObject;
    closeModalAction?: () => void;
    setEmptyFilterParams?: () => void;
} & IMutateFormProps<TFormFieldsWithTitles>;

// Generic form for adding or modifying react hook form object data
export default function MutateForm<TDefaultObject extends object, TFormFieldsWithTitles extends object>({
    defaultObject,
    closeModalAction,
    setEmptyFilterParams,
    formObjectSchema,
    useSaveMutation,
    deleteProps,
    successMessage,
    errorMessage,
    notModifiedMessage,
    formFieldsWithTitles,
    requiredFields,
}: IMutateForm<TDefaultObject, TFormFieldsWithTitles>) {
    const [saveData, {isLoading}] = useSaveMutation();
    const {
        useDeleteMutation,
        modalText: deleteModalText,
        successText: deleteSuccessText,
        successToastText: deleteSuccessToastText,
        errorToastText: deleteErrorToastTest,
    } = deleteProps ?? {};
    const [deleteObject, {data: deleteData, error: deleteError, isLoading: isDeleteLoading}] =
        useDeleteMutation?.() ?? [null, {}];
    const canDelete = !!(deleteProps && defaultObject);
    const [isDeleteModalVisible, setIsDeleteModalVisible] = useState(false);
    const runSaveData = (data) => {
        // submit the form values
        saveData(data)
            .unwrap()
            .then(() => {
                hdsToast.success(successMessage ?? "Tiedot tallennettu onnistuneesti!");
                closeModalAction?.();
                setEmptyFilterParams?.();
            })
            .catch((error) => {
                hdsToast.error(errorMessage ?? "Virhe tietojen tallentamisessa!");
                if (error.data.fields?.length > 0) {
                    error.data.fields.forEach((field) =>
                        formObject.setError(field.field, {type: "backend", message: field.message})
                    );
                }
            });
    };
    const handleConfirmedDeleteAction = () => {
        deleteObject(defaultObject)
            .unwrap()
            .then(() => {
                hdsToast.info(deleteSuccessToastText ?? "Tiedot poistettu onnistuneesti.");
                closeModalAction?.();
                setEmptyFilterParams?.();
            })
            .catch(() => {
                hdsToast.error(deleteErrorToastTest ?? "Virhe tietojen poistamisessa.");
                setIsDeleteModalVisible(true);
            });
    };

    // create form object
    const formObject = useForm({
        defaultValues: defaultObject ?? {},
        mode: "all",
        resolver: zodResolver(formObjectSchema),
    });

    useEffect(() => {
        // set initial focus
        const focusField = ((formFieldsWithTitles && Object.keys(formFieldsWithTitles)[0]) ?? "") as never;
        setTimeout(() => formObject.setFocus(focusField), 5);
    }, [formFieldsWithTitles]);

    const onFormSubmitValid = () => {
        // save the data
        runSaveData(formObject.getValues());
    };

    const onFormSubmitUnchanged = () => {
        // close without saving if the data has not changed
        hdsToast.success(notModifiedMessage ?? "Ei muutoksia tiedoissa.");
        close();
    };

    const close = () => {
        closeModalAction?.();
        // set filter params to default values if the form was opened to add new data
        !defaultObject && setEmptyFilterParams?.();
    };

    return (
        <>
            <FormProviderForm
                formObject={formObject}
                onSubmit={formObject.formState.isDirty ? onFormSubmitValid : onFormSubmitUnchanged}
            >
                {formFieldsWithTitles &&
                    Object.entries(formFieldsWithTitles).map(([field, title]) => (
                        <TextInput
                            key={field}
                            name={field}
                            label={title}
                            required={requiredFields?.includes(field)}
                        />
                    ))}
                <div className="row row--buttons">
                    <Button
                        theme={ButtonPresetTheme.Black}
                        iconStart={<IconArrowLeft />}
                        onClick={close}
                    >
                        Peruuta
                    </Button>
                    {canDelete && (
                        <DeleteButton
                            isLoading={false}
                            onClick={() => setIsDeleteModalVisible(true)}
                        />
                    )}
                    <SaveButton
                        isLoading={isLoading}
                        type="submit"
                        buttonText="Tallenna"
                        disabled={!formObject.formState.isValid}
                    />
                </div>
            </FormProviderForm>
            {canDelete && (
                <ConfirmDialogModal
                    modalText={typeof deleteModalText === "function" ? deleteModalText(defaultObject) : deleteModalText}
                    successText={deleteSuccessText}
                    buttonText="Poista"
                    isVisible={isDeleteModalVisible}
                    setIsVisible={setIsDeleteModalVisible}
                    data={deleteData}
                    error={deleteError}
                    isLoading={isDeleteLoading}
                    confirmAction={handleConfirmedDeleteAction}
                    cancelAction={() => setIsDeleteModalVisible(false)}
                />
            )}
        </>
    );
}
