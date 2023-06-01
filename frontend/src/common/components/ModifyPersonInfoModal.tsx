import {zodResolver} from "@hookform/resolvers/zod/dist/zod";
import {Button, Dialog, IconArrowLeft} from "hds-react";
import {Dispatch, SetStateAction, useEffect} from "react";
import {useForm} from "react-hook-form";
import {z} from "zod";
import {useSaveOwnerMutation} from "../../app/services";
import {IOwner, OwnerSchema} from "../schemas";
import {hdsToast, validateBusinessId, validateSocialSecurityNumber} from "../utils";
import TextInput from "./form/TextInput";
import SaveButton from "./SaveButton";

interface IOwnerMutateForm {
    owner: IOwner;
    closeModalAction: () => void;
}
const OwnerMutateForm = ({owner, closeModalAction}: IOwnerMutateForm) => {
    const [saveOwner, {isLoading: isSaveOwnerLoading}] = useSaveOwnerMutation();
    const runSaveOwner = (data) => {
        // submit the form values
        saveOwner({data: data})
            .unwrap()
            .then((payload) => {
                hdsToast.success("Omistajan tiedot tallennettu onnistuneesti!");
                closeModalAction();
            })
            .catch((error) => {
                hdsToast.error("Virhe omistajan tietojen tallentamisessa!");
                error.data.fields.forEach((field) =>
                    ownerFormObject.setError(field.field, {type: "backend", message: field.message})
                );
            });
    };

    const resolver = (data, context, options) => {
        // validate the identifier field
        return zodResolver(
            OwnerSchema.superRefine((data, ctx) => {
                if (!validateSocialSecurityNumber(data.identifier) && !validateBusinessId(data.identifier)) {
                    ctx.addIssue({
                        code: z.ZodIssueCode.custom,
                        path: ["identifier"],
                        message: "Virheellinen henkilö- tai Y-tunnus",
                    });
                }
            })
        )(data, context, {...options, mode: "sync"});
    };

    const ownerFormObject = useForm({
        defaultValues: owner,
        mode: "all",
        resolver: resolver,
    });

    // helper values
    const identifierValue = ownerFormObject.watch("identifier");
    const hasFormChanged =
        ownerFormObject.formState.isDirty && JSON.stringify(owner) !== JSON.stringify(ownerFormObject.getValues());
    const isMalformedIdentifier = ownerFormObject.formState.errors.identifier?.type === "custom";
    const isIdentifierEmpty = identifierValue === "";
    const isBackendErrorInIdentifier = ownerFormObject.formState.errors.identifier?.type === "backend";
    const isOtherErrorsThanIdentifier = Object.keys(ownerFormObject.formState.errors).some(
        (field) => field !== "identifier"
    );

    // booleans to determine if submitting the form is enabled and with or without warnings
    const isSaveWithWarning = isMalformedIdentifier && !isOtherErrorsThanIdentifier && !isIdentifierEmpty;
    const isSaveDisabled =
        isOtherErrorsThanIdentifier || isIdentifierEmpty || isBackendErrorInIdentifier || !hasFormChanged;

    useEffect(() => {
        // validate the initial form values
        ownerFormObject.trigger();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const onFormSubmitValid = () => {
        runSaveOwner(ownerFormObject.getValues());
    };

    const onFormSubmitInvalid = (errors) => {
        if (isSaveWithWarning) {
            // submit with warning
            runSaveOwner(ownerFormObject.getValues());
        }
    };

    return (
        <>
            <form onSubmit={ownerFormObject.handleSubmit(onFormSubmitValid, onFormSubmitInvalid)}>
                <TextInput
                    name="name"
                    label="Nimi"
                    formObject={ownerFormObject}
                    required
                />
                <TextInput
                    name="identifier"
                    label="Henkilö- tai Y-tunnus"
                    formObject={ownerFormObject}
                    required
                />
                <TextInput
                    name="email"
                    label="Sähköpostiosoite"
                    formObject={ownerFormObject}
                />
                {
                    // show warning when identifier is invalid
                    isSaveWithWarning && !isSaveDisabled && (
                        <p className="error-message">
                            "{identifierValue}" on virheellinen henkilö- tai Y-tunnus. Tallennetaanko silti?
                        </p>
                    )
                }
                <div className="row row--buttons">
                    <Button
                        theme="black"
                        iconLeft={<IconArrowLeft />}
                        onClick={closeModalAction}
                    >
                        Peruuta
                    </Button>

                    <SaveButton
                        isLoading={isSaveOwnerLoading}
                        type="submit"
                        buttonText={isSaveWithWarning ? "Tallenna silti" : "Tallenna"}
                        disabled={isSaveDisabled}
                    />
                </div>
            </form>

            <Dialog.ActionButtons />
        </>
    );
};

interface IModifyPersonInfoModalProps {
    owner: IOwner;
    isVisible: boolean;
    setIsVisible: Dispatch<SetStateAction<boolean>>;
}

export default function ModifyPersonInfoModal({owner, isVisible, setIsVisible}: IModifyPersonInfoModalProps) {
    return (
        <Dialog
            id="modify-person-info-modal"
            closeButtonLabelText=""
            aria-labelledby=""
            isOpen={isVisible}
            close={() => setIsVisible(false)}
            boxShadow
        >
            <Dialog.Header
                id="modify-person-info-modal__header"
                title="Muokkaa henkilötietoja"
            />
            <Dialog.Content>
                <OwnerMutateForm
                    owner={owner}
                    closeModalAction={() => setIsVisible(false)}
                />
            </Dialog.Content>
        </Dialog>
    );
}
