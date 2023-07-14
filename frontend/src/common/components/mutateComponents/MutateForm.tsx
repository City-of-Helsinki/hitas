import {zodResolver} from "@hookform/resolvers/zod";
import {Button, IconArrowLeft} from "hds-react";
import {useEffect} from "react";
import {useForm} from "react-hook-form";
import {hdsToast} from "../../utils";
import {FormProviderForm, TextInput} from "../forms";
import SaveButton from "../SaveButton";

export interface IMutateFormProps<TFormFieldsWithTitles extends object> {
    formObjectSchema;
    useSaveMutation;
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
    successMessage,
    errorMessage,
    notModifiedMessage,
    formFieldsWithTitles,
    requiredFields,
}: IMutateForm<TDefaultObject, TFormFieldsWithTitles>) {
    const [saveData, {isLoading}] = useSaveMutation();
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
                    theme="black"
                    iconLeft={<IconArrowLeft />}
                    onClick={close}
                >
                    Peruuta
                </Button>
                <SaveButton
                    isLoading={isLoading}
                    type="submit"
                    buttonText="Tallenna"
                    disabled={!formObject.formState.isValid}
                />
            </div>
        </FormProviderForm>
    );
}
