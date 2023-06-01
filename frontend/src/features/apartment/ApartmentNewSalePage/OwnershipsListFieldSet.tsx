import {Button, Dialog, Fieldset, IconArrowLeft, IconCrossCircle, IconPlus} from "hds-react";
import {useFieldArray, useForm, useFormContext} from "react-hook-form";
import {v4 as uuidv4} from "uuid";

import {zodResolver} from "@hookform/resolvers/zod/dist/zod";
import {useRef, useState} from "react";
import {z} from "zod";
import {useGetOwnersQuery, useSaveOwnerMutation} from "../../../app/services";
import {NumberInput, RelatedModelInput} from "../../../common/components/form";
import TextInput from "../../../common/components/form/TextInput";
import SaveButton from "../../../common/components/SaveButton";
import SimpleErrorMessage from "../../../common/components/SimpleErrorMessage";
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

const OwnershipsListFieldSet = () => {
    const formObject = useFormContext();

    const {fields, append, remove} = useFieldArray({
        name: "ownerships",
        control: formObject.control,
        rules: {required: "Kauppatapahtumassa täytyy olla ainakin yksi omistajuus!"},
    });
    formObject.register("ownerships");

    // Blank Ownership. This is appended to the list when user clicks "New ownership"
    const emptyOwnership = {key: uuidv4(), owner: {id: ""} as IOwner, percentage: 100};

    const formErrors = OwnershipsListSchema.safeParse(formObject.getValues("ownerships"));

    return (
        <Fieldset
            className={`ownerships-fieldset ${formErrors.success ? "" : "error"}`}
            heading="Omistajuudet *"
        >
            <ul className="ownerships-list">
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
                                    RelatedModelMutateComponent={OwnerMutateForm}
                                />
                            </div>
                            <div className="percentage">
                                <NumberInput
                                    name={`ownerships.${index}.percentage`}
                                    fractionDigits={2}
                                    formObject={formObject}
                                    required
                                />
                                <span>%</span>
                            </div>
                            <div className="icon--remove">
                                <IconCrossCircle
                                    size="m"
                                    onClick={() => remove(index)}
                                />
                            </div>
                        </li>
                    ))}
                </>
            </ul>

            <>
                {!formErrors.success &&
                    formErrors.error &&
                    formErrors.error.issues.map((e) => (
                        <SimpleErrorMessage
                            key={`${e.code}-${e.message}`}
                            errorMessage={e.message}
                        />
                    ))}
            </>

            <div className="row row--buttons">
                <Button
                    iconLeft={<IconPlus />}
                    variant={formObject.watch("ownerships").length > 0 ? "secondary" : "primary"}
                    theme="black"
                    onClick={() => append(emptyOwnership)}
                >
                    Lisää uusi omistajuus rivi
                </Button>
            </div>
        </Fieldset>
    );
};

export default OwnershipsListFieldSet;
