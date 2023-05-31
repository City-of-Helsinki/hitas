import {zodResolver} from "@hookform/resolvers/zod/dist/zod";
import {Button, Dialog, IconArrowLeft} from "hds-react";
import {Dispatch, SetStateAction, useState} from "react";
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
    const [isSubmitted, setIsSubmitted] = useState(false);

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

    const ownerFormObject = useForm({
        defaultValues: owner,
        mode: "all",
        resolver: zodResolver(OwnerSchema),
    });

    const onFormSubmitValid = () => {
        setIsSubmitted(true);
        runSaveOwner(ownerFormObject.getValues());
    };

    const onFormSubmitInvalid = (errors) => {
        if (errors.identifier && errors.identifier.type === z.ZodIssueCode.custom) {
            setIsInvalidSSNAllowed(true);
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
                    // If valid identifier values are required and the identifier
                    // is not one, show prompt for confirmation when submitting
                    isInvalidSSNAllowed &&
                        !validateSocialSecurityNumber(ownerFormObject.getValues("identifier")) &&
                        isSubmitted && (
                            <p className="error-message">
                                "{ownerFormObject.getValues("identifier")}" ei ole oikea sosiaaliturvatunnus.
                                Tallennetaanko silti?
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
