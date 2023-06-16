import {zodResolver} from "@hookform/resolvers/zod";
import {Button, Dialog, IconArrowLeft} from "hds-react";
import {useEffect} from "react";
import {useForm} from "react-hook-form";
import {useSaveManagerMutation} from "../../app/services";
import {IPropertyManager, PropertyManagerSchema} from "../schemas";
import {hdsToast} from "../utils";
import {TextInput} from "./form";
import SaveButton from "./SaveButton";

interface IManagerMutateForm {
    defaultObject?: IPropertyManager;
    closeModalAction: () => void;
    setDefaultFilterParams?: () => void;
}
export default function ManagerMutateForm({
    defaultObject: manager,
    closeModalAction,
    setDefaultFilterParams,
}: IManagerMutateForm) {
    const [saveManager, {isLoading: isSaveManagerLoading}] = useSaveManagerMutation();
    const runSaveManager = (data) => {
        // submit the form values
        saveManager(data)
            .unwrap()
            .then(() => {
                hdsToast.success("Isännöitsijän tiedot tallennettu onnistuneesti!");
                closeModalAction();
                setDefaultFilterParams && setDefaultFilterParams();
            })
            .catch((error) => {
                hdsToast.error("Virhe isännöitsijän tietojen tallentamisessa!");
                if (error.data.fields && error.data.fields.length > 0) {
                    error.data.fields.forEach((field) =>
                        managerFormObject.setError(field.field, {type: "backend", message: field.message})
                    );
                }
            });
    };

    const managerFormObject = useForm({
        ...(manager && {defaultValues: manager}),
        mode: "all",
        resolver: zodResolver(PropertyManagerSchema),
    });

    useEffect(() => {
        // validate the initial form values
        managerFormObject.trigger().then(() => {
            // set initial focus
            setTimeout(() => managerFormObject.setFocus("name"), 5);
        });
        // eslint-disable-next-line
    }, []);

    const onFormSubmitValid = () => {
        runSaveManager(managerFormObject.getValues());
    };

    return (
        <>
            <form onSubmit={managerFormObject.handleSubmit(onFormSubmitValid)}>
                <TextInput
                    name="name"
                    label="Nimi"
                    formObject={managerFormObject}
                    required
                />
                <TextInput
                    name="email"
                    label="Sähköpostiosoite"
                    formObject={managerFormObject}
                />
                {
                    // show info about the disabled saving of the unmodified form
                    !managerFormObject.formState.isDirty && manager && (
                        <p className="error-message">Lomakkeen tietoja ei ole muutettu</p>
                    )
                }
                <div className="row row--buttons">
                    <Button
                        theme="black"
                        iconLeft={<IconArrowLeft />}
                        onClick={() => {
                            closeModalAction();
                            if (setDefaultFilterParams && !manager) {
                                setDefaultFilterParams();
                            }
                        }}
                    >
                        Peruuta
                    </Button>
                    <SaveButton
                        isLoading={isSaveManagerLoading}
                        type="submit"
                        buttonText="Tallenna"
                        disabled={!managerFormObject.formState.isDirty || !managerFormObject.formState.isValid}
                    />
                </div>
            </form>

            <Dialog.ActionButtons />
        </>
    );
}
