import {Button, Dialog, Fieldset, IconAlertCircleFill, IconArrowLeft, IconCrossCircle, IconPlus} from "hds-react";
import {useFieldArray, useForm} from "react-hook-form";
import {v4 as uuidv4} from "uuid";

import {zodResolver} from "@hookform/resolvers/zod/dist/zod";
import {useRef, useState} from "react";
import {z} from "zod";
import {useGetOwnersQuery, useSaveOwnerMutation} from "../../../app/services";
import {NumberInput, RelatedModelInput} from "../../../common/components/form";
import TextInput from "../../../common/components/form/TextInput";
import SaveButton from "../../../common/components/SaveButton";
import {IOwner, OwnerSchema, OwnershipsListSchema} from "../../../common/schemas";
import {formatOwner, hdsToast, validateSocialSecurityNumber} from "../../../common/utils";

const OwnerMutateForm = ({formObject, formObjectFieldPath, cancelButtonAction, closeModalAction}) => {
    const [isInvalidSSNAllowed, setIsInvalidSSNAllowed] = useState(false);

    const [saveOwner, {isLoading: isSaveOwnerLoading}] = useSaveOwnerMutation();
    const runSaveOwner = (data) => {
        saveOwner({data: data})
            .unwrap()
            .then((payload) => {
                hdsToast.success("Omistaja luotu onnistuneesti!");
                formObject.setValue(formObjectFieldPath, payload);
                cancelButtonAction();
                closeModalAction();
            })
            .catch((error) => {
                hdsToast.error("Virhe omistajan luonnissa!");
                error.data.fields.forEach((field) =>
                    ownerFormObject.setError(field.field, {type: "custom", message: field.message})
                );
            });
    };

    const initialFormData = {name: "", identifier: "", email: ""};

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
        // Dispatch submit event, as the "Tallenna"-button isn't inside the sale form element
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
                    onClick={cancelButtonAction}
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

const OwnershipsListFieldSet = ({formObject, disabled}) => {
    const {fields, append, remove} = useFieldArray({
        name: "ownerships",
        control: formObject.control,
        rules: {required: "Kauppatapahtumassa täytyy olla ainakin yksi omistajuus!"},
    });
    formObject.register("ownerships");

    // Blank Ownership. This is appended to the list when user clicks "New ownership"
    const emptyOwnership = {key: uuidv4(), owner: {id: ""} as IOwner, percentage: 100};

    const ownerships = formObject.getValues("ownerships");
    const formErrors = OwnershipsListSchema.safeParse(formObject.getValues("ownerships"));
    const isFormInvalid = !formErrors.success;

    return (
        <Fieldset
            className={`ownerships-fieldset ${isFormInvalid ? "error" : ""}`}
            heading="Omistajuudet *"
        >
            <ul className="ownerships-list">
                {ownerships.length ? (
                    <>
                        <li>
                            <legend className="ownership-headings">
                                <span>Omistaja *</span>
                                <span>Osuus *</span>
                            </legend>
                        </li>
                        {fields.map((field, index) => (
                            <li
                                className="ownership-item"
                                key={field.id}
                            >
                                <div className="owner">
                                    <RelatedModelInput
                                        label="Omistaja"
                                        required
                                        queryFunction={useGetOwnersQuery}
                                        relatedModelSearchField="name"
                                        formObject={formObject}
                                        formObjectFieldPath={`ownerships.${index}.owner`}
                                        formatFormObjectValue={(obj) => (obj.id ? formatOwner(obj) : "")}
                                        disabled={disabled}
                                        RelatedModelMutateComponent={OwnerMutateForm}
                                    />
                                </div>
                                <div className="percentage">
                                    <NumberInput
                                        name={`ownerships.${index}.percentage`}
                                        fractionDigits={2}
                                        formObject={formObject}
                                        required
                                        disabled={disabled}
                                    />
                                    <span>%</span>
                                </div>
                                <div className={`icon--remove${disabled ? " disabled" : ""}`}>
                                    <IconCrossCircle
                                        size="m"
                                        onClick={() => (disabled ? null : remove(index))}
                                    />
                                </div>
                            </li>
                        ))}
                    </>
                ) : (
                    <div
                        className={isFormInvalid ? "error-text" : ""}
                        style={{textAlign: "center"}}
                    >
                        <IconAlertCircleFill />
                        Asunnolla ei ole omistajuuksia
                        <IconAlertCircleFill />
                    </div>
                )}
            </ul>
            {!formErrors.success && formErrors.error ? (
                <>
                    {formErrors.error.issues.map((e) => (
                        <span
                            key={`${e.code}-${e.message}`}
                            className="error-text"
                        >
                            {e.message}
                        </span>
                    ))}
                </>
            ) : null}
            <div className="row row--buttons">
                <Button
                    iconLeft={<IconPlus />}
                    variant={ownerships.length > 0 ? "secondary" : "primary"}
                    theme="black"
                    onClick={() => append(emptyOwnership)}
                    disabled={disabled}
                >
                    Lisää uusi omistajuus rivi
                </Button>
            </div>
        </Fieldset>
    );
};

export default OwnershipsListFieldSet;
