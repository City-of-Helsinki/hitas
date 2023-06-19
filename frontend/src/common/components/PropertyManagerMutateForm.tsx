import {zodResolver} from "@hookform/resolvers/zod";
import {Button, IconArrowLeft} from "hds-react";
import {useEffect} from "react";
import {useForm} from "react-hook-form";
import {useSavePropertyManagerMutation} from "../../app/services";
import {IPropertyManager, PropertyManagerSchema} from "../schemas";
import {hdsToast} from "../utils";
import {TextInput} from "./form";
import SaveButton from "./SaveButton";

interface IPropertyManagerMutateForm {
    defaultObject?: IPropertyManager;
    closeModalAction: () => void;
    setDefaultFilterParams?: () => void;
}
export default function PropertyManagerMutateForm({
    defaultObject: propertyManager,
    closeModalAction,
    setDefaultFilterParams,
}: IPropertyManagerMutateForm) {
    const [savePropertyManager, {isLoading: isSavePropertyManagerLoading}] = useSavePropertyManagerMutation();
    const runSavePropertyManager = (data) => {
        // submit the form values
        savePropertyManager(data)
            .unwrap()
            .then(() => {
                hdsToast.success("Isännöitsijän tiedot tallennettu onnistuneesti!");
                closeModalAction();
                setDefaultFilterParams?.();
            })
            .catch((error) => {
                hdsToast.error("Virhe isännöitsijän tietojen tallentamisessa!");
                if (error.data.fields?.length > 0) {
                    error.data.fields.forEach((field) =>
                        propertyManagerFormObject.setError(field.field, {type: "backend", message: field.message})
                    );
                }
            });
    };

    const propertyManagerFormObject = useForm({
        defaultValues: propertyManager,
        mode: "all",
        resolver: zodResolver(PropertyManagerSchema),
    });

    useEffect(() => {
        // validate the initial form values
        propertyManagerFormObject.trigger().then(() => {
            // set initial focus
            setTimeout(() => propertyManagerFormObject.setFocus("name"), 5);
        });
        // eslint-disable-next-line
    }, []);

    const onFormSubmitValid = () => {
        // save the data
        runSavePropertyManager(propertyManagerFormObject.getValues());
    };

    const onFormSubmitUnchanged = () => {
        // close without saving if the data has not changed
        hdsToast.success("Ei muutoksia isännöitsijän tiedoissa.");
        close();
    };

    const close = () => {
        closeModalAction();
        !propertyManager && setDefaultFilterParams?.();
    };

    return (
        <>
            <form
                onSubmit={
                    propertyManagerFormObject.formState.isDirty
                        ? propertyManagerFormObject.handleSubmit(onFormSubmitValid)
                        : propertyManagerFormObject.handleSubmit(onFormSubmitUnchanged)
                }
            >
                <TextInput
                    name="name"
                    label="Nimi"
                    formObject={propertyManagerFormObject}
                    required
                />
                <TextInput
                    name="email"
                    label="Sähköpostiosoite"
                    formObject={propertyManagerFormObject}
                />
                <div className="row row--buttons">
                    <Button
                        theme="black"
                        iconLeft={<IconArrowLeft />}
                        onClick={close}
                    >
                        Peruuta
                    </Button>
                    <SaveButton
                        isLoading={isSavePropertyManagerLoading}
                        type="submit"
                        buttonText="Tallenna"
                        disabled={!propertyManagerFormObject.formState.isValid}
                    />
                </div>
            </form>
        </>
    );
}
