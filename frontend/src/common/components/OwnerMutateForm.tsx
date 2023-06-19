import {zodResolver} from "@hookform/resolvers/zod/dist/zod";
import {Button, IconArrowLeft} from "hds-react";
import {useEffect, useState} from "react";
import {useForm} from "react-hook-form";
import {z} from "zod";
import {useSaveOwnerMutation} from "../../app/services";
import {IOwner, OwnerSchema} from "../schemas";
import {hdsToast, validateBusinessId, validateSocialSecurityNumber} from "../utils";
import {Checkbox, TextInput} from "./form";
import SaveButton from "./SaveButton";

interface IOwnerMutateForm {
    defaultObject?: IOwner;
    closeModalAction: () => void;
    setDefaultFilterParams?: () => void;
}
export default function OwnerMutateForm({
    defaultObject: owner,
    closeModalAction,
    setDefaultFilterParams,
}: IOwnerMutateForm) {
    const [isInitialIdentifierValid, setIsInitialIdentifierValid] = useState<boolean>(false);
    const [saveOwner, {isLoading: isSaveOwnerLoading}] = useSaveOwnerMutation();
    const runSaveOwner = (data) => {
        // submit the form values
        saveOwner({data: data})
            .unwrap()
            .then(() => {
                hdsToast.success("Omistajan tiedot tallennettu onnistuneesti!");
                closeModalAction();
                setDefaultFilterParams?.();
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
        isBackendErrorInIdentifier;

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
        // save the data
        runSaveOwner(ownerFormObject.getValues());
    };

    const onFormSubmitInvalid = () => {
        if (isSaveWithWarning) {
            // save with warning
            runSaveOwner(ownerFormObject.getValues());
        }
    };

    const onFormSubmitUnchanged = () => {
        // close without saving if the data has not changed
        hdsToast.success("Ei muutoksia omistajan tiedoissa.");
        close();
    };

    const close = () => {
        closeModalAction();
        !owner && setDefaultFilterParams?.();
    };

    return (
        <>
            <form
                onSubmit={
                    hasFormChanged
                        ? ownerFormObject.handleSubmit(onFormSubmitValid, onFormSubmitInvalid)
                        : ownerFormObject.handleSubmit(onFormSubmitUnchanged, onFormSubmitUnchanged)
                }
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
                <div className="row row--buttons">
                    <Button
                        theme="black"
                        iconLeft={<IconArrowLeft />}
                        onClick={close}
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
        </>
    );
}
