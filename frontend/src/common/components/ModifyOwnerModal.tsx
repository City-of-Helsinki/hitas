import {zodResolver} from "@hookform/resolvers/zod/dist/zod";
import {Button, Dialog, IconArrowLeft} from "hds-react";
import {Dispatch, SetStateAction, useEffect, useState} from "react";
import {useForm} from "react-hook-form";
import {z} from "zod";
import {useSaveOwnerMutation} from "../../app/services";
import {IOwner, OwnerSchema} from "../schemas";
import {hdsToast, validateBusinessId, validateSocialSecurityNumber} from "../utils";
import {Checkbox, TextInput} from "./form";
import SaveButton from "./SaveButton";

interface IOwnerMutateForm {
    owner: IOwner;
    closeModalAction: () => void;
}
const OwnerMutateForm = ({owner, closeModalAction}: IOwnerMutateForm) => {
    const [isInitialIdentifierValid, setIsInitialIdentifierValid] = useState<boolean>(false);
    const [saveOwner, {isLoading: isSaveOwnerLoading}] = useSaveOwnerMutation();
    const runSaveOwner = (data) => {
        // submit the form values
        saveOwner({data: data})
            .unwrap()
            .then(() => {
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

    const resolver = async (data, context, options) => {
        // validate the form
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
    const identifierValue = ownerFormObject.watch("identifier");

    // helper booleans for special saving controls with invalid data
    const hasFormChanged = ownerFormObject.formState.isDirty;
    const isMalformedIdentifier = !!ownerFormObject.formState.errors.identifier;
    const isIdentifierEmpty = identifierValue === "";
    const isBackendErrorInIdentifier = ownerFormObject.formState.errors.identifier?.type === "backend";
    const isOtherErrorsThanIdentifier = Object.keys(ownerFormObject.formState.errors).some(
        (field) => field !== "identifier"
    );

    // enable submitting malformed non-empty identifier if it wasn't valid initially and other fields are valid
    const isSaveWithWarning =
        isMalformedIdentifier && !isInitialIdentifierValid && !isOtherErrorsThanIdentifier && !isIdentifierEmpty;
    // disable submitting in the following cases:
    const isSaveDisabled =
        isOtherErrorsThanIdentifier ||
        isIdentifierEmpty ||
        (isMalformedIdentifier && isInitialIdentifierValid) ||
        isBackendErrorInIdentifier ||
        !hasFormChanged;

    useEffect(() => {
        // validate the initial form values
        ownerFormObject.trigger().then(() => {
            // set the initial identifier validity
            setIsInitialIdentifierValid(!ownerFormObject.formState.errors.identifier);
            // set initial focus
            setTimeout(() => ownerFormObject.setFocus("name"), 5);
        });
        // eslint-disable-next-line
    }, []);

    const onFormSubmitValid = () => {
        runSaveOwner(ownerFormObject.getValues());
    };

    const onFormSubmitInvalid = () => {
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
                <Checkbox
                    label="Turvakielto"
                    name="non_disclosure"
                    formObject={ownerFormObject}
                />
                {
                    // show warning when saving malformed identifier is enabled
                    isSaveWithWarning && !isSaveDisabled && (
                        <p className="error-message">
                            "{identifierValue}" on virheellinen henkilö- tai Y-tunnus. Tallennetaanko silti?
                        </p>
                    )
                }
                {
                    // show info about the disabled saving of the unmodified form
                    !hasFormChanged && <p className="error-message">Lomakkeen tietoja ei ole muutettu</p>
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

export default function ModifyOwnerModal({owner, isVisible, setIsVisible}: IModifyPersonInfoModalProps) {
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
