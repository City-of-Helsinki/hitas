import {zodResolver} from "@hookform/resolvers/zod/dist/zod";
import {Button, IconArrowLeft} from "hds-react";
import {useEffect, useRef} from "react";
import {useForm} from "react-hook-form";
import {z} from "zod";
import {IOwner, OwnerSchema} from "../../schemas";
import {useSaveOwnerMutation} from "../../services";
import {hdsToast, setAPIErrorsForFormFields, validateBusinessId, validateSocialSecurityNumber} from "../../utils";
import {CheckboxInput, SaveFormButton, TextInput} from "../forms";
import FormProviderForm from "../forms/FormProviderForm";

interface IOwnerMutateForm {
    defaultObject?: IOwner;
    closeModalAction: () => void;
    setEmptyFilterParams?: () => void;
}
export default function OwnerMutateForm({
    defaultObject: owner,
    closeModalAction,
    setEmptyFilterParams,
}: IOwnerMutateForm) {
    const isInitialIdentifierValid = owner !== undefined && validateSocialSecurityNumber(owner.identifier);
    const [saveOwner, {isLoading: isSaveOwnerLoading}] = useSaveOwnerMutation();

    const closeModal = () => {
        closeModalAction();
        !owner && setEmptyFilterParams?.();
    };

    const resolver = (data, context, options) => {
        return zodResolver(
            OwnerSchema.omit({id: true}).superRefine((data, ctx) => {
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

    const formRef = useRef<HTMLFormElement>(null);
    const formObject = useForm({
        defaultValues: owner,
        mode: "all",
        resolver: resolver,
    });

    // formState needs to be read before a render in order to enable the state update
    const {
        formState: {isDirty: isFormDirty, errors: formErrors},
    } = formObject;

    // If the initial identifier is invalid, show a warning when saving
    const isInvalidIdentifierSaveWarningShown =
        !isInitialIdentifierValid && !!formErrors.identifier && formErrors.identifier.type === "custom";
    // Disable saving if form has any errors
    // With the exception, that if the initial identifier is invalid, it can stay invalid
    const isSaveDisabled =
        !!Object.keys(formErrors).length &&
        (isInitialIdentifierValid ||
            (!isInitialIdentifierValid &&
                ((!!formErrors.identifier && formErrors.identifier.type !== "custom") ||
                    Object.keys(formErrors).some((field) => field !== "identifier"))));

    const runSaveOwner = () => {
        if (!isFormDirty) {
            hdsToast.info("Ei muutoksia omistajan tiedoissa.");
            closeModalAction();
            return;
        }

        saveOwner({data: formObject.getValues()})
            .unwrap()
            .then(() => {
                hdsToast.success("Omistajan tiedot tallennettu onnistuneesti!");
                closeModalAction();
                setEmptyFilterParams?.();
            })
            .catch((error) => {
                hdsToast.error("Virhe omistajan tietojen tallentamisessa!");
                setAPIErrorsForFormFields(formObject, error);
            });
    };

    const onFormSubmitValid = () => {
        runSaveOwner();
    };

    const onFormSubmitInvalid = () => {
        if (isInvalidIdentifierSaveWarningShown) {
            runSaveOwner();
        }
    };

    useEffect(() => {
        // Set initial focus to the "name" field
        formObject.trigger().then(() => setTimeout(() => formObject.setFocus("name"), 5));
        // eslint-disable-next-line
    }, []);

    return (
        <FormProviderForm
            formObject={formObject}
            formRef={formRef}
            onSubmit={onFormSubmitValid}
            onSubmitError={onFormSubmitInvalid}
        >
            <TextInput
                name="name"
                label="Nimi"
                required
            />
            <TextInput
                name="identifier"
                label="Henkilö- tai Y-tunnus"
                required
            />
            <TextInput
                name="email"
                label="Sähköpostiosoite"
            />
            <CheckboxInput
                label="Turvakielto"
                name="non_disclosure"
            />
            {
                // show warning when saving malformed identifier is enabled
                isInvalidIdentifierSaveWarningShown && !isSaveDisabled && (
                    <p className="error-message">
                        '{formObject.watch("identifier")}' on virheellinen henkilö- tai Y-tunnus.
                        <br />
                        Tallennetaanko silti?
                    </p>
                )
            }
            <div className="row row--buttons">
                <Button
                    theme="black"
                    iconLeft={<IconArrowLeft />}
                    onClick={closeModal}
                >
                    Peruuta
                </Button>

                <SaveFormButton
                    formRef={formRef}
                    isLoading={isSaveOwnerLoading}
                    buttonText={isInvalidIdentifierSaveWarningShown ? "Tallenna silti" : "Tallenna"}
                    disabled={isSaveDisabled}
                />
            </div>
        </FormProviderForm>
    );
}
