import {zodResolver} from "@hookform/resolvers/zod/dist/zod";
import {Button, Dialog, IconArrowLeft} from "hds-react";
import {Dispatch, SetStateAction, useRef, useState} from "react";
import {useForm} from "react-hook-form";
import {z} from "zod";
import {useSaveOwnerMutation} from "../../app/services";
import TextInput from "../../common/components/form/TextInput";
import SaveButton from "../../common/components/SaveButton";
import {IOwner, OwnerSchema} from "../../common/schemas";
import {hdsToast, validateSocialSecurityNumber} from "../../common/utils";

interface IOwnerMutateForm {
    owner: IOwner;
    closeModalAction: () => void;
}
const OwnerMutateForm = ({owner, closeModalAction}: IOwnerMutateForm) => {
    const [isInvalidSSNAllowed, setIsInvalidSSNAllowed] = useState(false);

    const [saveOwner, {isLoading: isSaveOwnerLoading}] = useSaveOwnerMutation();
    const runSaveOwner = (data) => {
        saveOwner({data: data})
            .unwrap()
            .then((payload) => {
                hdsToast.success("Omistajan tiedot muutettu onnistuneesti!");
                closeModalAction();
            })
            .catch((error) => {
                hdsToast.error("Virhe omistajan tietojen muuttamisessa!");
                error.data.fields.forEach((field) =>
                    ownerFormObject.setError(field.field, {type: "custom", message: field.message})
                );
            });
    };

    const initialFormData = {...owner};

    const resolver = (data, context, options) => {
        return zodResolver(
            OwnerSchema.superRefine((data, ctx) => {
                if (!isInvalidSSNAllowed && !validateSocialSecurityNumber(data.identifier)) {
                    ctx.addIssue({
                        code: z.ZodIssueCode.custom,
                        path: ["identifier"],
                        message: "Virheellinen sosiaaliturvatunnus",
                    });
                }
            })
        )(data, context, {...options, mode: "sync"});
    };

    const ownerFormObject = useForm({
        defaultValues: {...initialFormData},
        mode: "all",
        resolver: resolver,
    });

    const formRef = useRef<HTMLFormElement | null>(null);

    const onFormSubmitValid = () => {
        runSaveOwner(ownerFormObject.getValues());
    };

    const onFormSubmitInvalid = (errors) => {
        if (errors.identifier && errors.identifier.type === z.ZodIssueCode.custom) {
            setIsInvalidSSNAllowed(true);
        }
    };

    const handleSaveButtonClick = () => {
        // Dispatch submit event, as the "Tallenna"-button isn't inside the form element
        formRef.current && formRef.current.dispatchEvent(new Event("submit", {cancelable: true, bubbles: true}));
    };

    return (
        <>
            <form
                ref={formRef}
                onSubmit={ownerFormObject.handleSubmit(onFormSubmitValid, onFormSubmitInvalid)}
            >
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
            </form>

            <Dialog.ActionButtons>
                <Button
                    theme="black"
                    size="small"
                    iconLeft={<IconArrowLeft />}
                    onClick={closeModalAction}
                >
                    Peruuta
                </Button>
                <SaveButton
                    onClick={handleSaveButtonClick}
                    isLoading={isSaveOwnerLoading}
                    size="small"
                />
            </Dialog.ActionButtons>
        </>
    );
};

interface IModifyPersonInfoModalProps {
    owner: IOwner;
    isVisible: boolean;
    setIsVisible: Dispatch<SetStateAction<boolean>>;
}
export const ModifyPersonInfoModal = ({owner, isVisible, setIsVisible}: IModifyPersonInfoModalProps) => {
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
};
