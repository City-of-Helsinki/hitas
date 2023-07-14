import {useState} from "react";

import {zodResolver} from "@hookform/resolvers/zod";
import {Button} from "hds-react";
import {SubmitHandler, useForm} from "react-hook-form";

import {IOwner, OwnerSchema} from "../schemas";
import {validateSocialSecurityNumber} from "../utils";
import {CheckboxInput, TextInput} from "./forms";
import FormProviderForm from "./forms/FormProviderForm";
import {SaveButton} from "./index";

type NewOwnerFormProps = {
    confirmAction: (unknown) => unknown;
    cancelAction: (unknown) => unknown;
    isInvalidSSNAllowed: boolean;
    isLoading: boolean;
};

const NewOwnerForm = ({confirmAction, cancelAction, isInvalidSSNAllowed, isLoading}: NewOwnerFormProps) => {
    const [isSubmitted, setIsSubmitted] = useState(false);
    const initialFormData = {
        name: "",
        identifier: "",
        email: "",
        non_disclosure: false,
    };

    const formObject = useForm<IOwner>({
        defaultValues: initialFormData,
        mode: "all",
        resolver: zodResolver(OwnerSchema),
    });
    const {
        formState: {isDirty, isValid},
    } = formObject;
    const onValidSubmit: SubmitHandler<IOwner> = (data) => {
        setIsSubmitted(true);
        confirmAction(data);
    };

    return (
        <FormProviderForm
            formObject={formObject}
            className="hitas-form hitas-form--owner"
            onSubmit={onValidSubmit}
        >
            <TextInput
                name="name"
                label="Nimi"
                required
            />
            <TextInput
                name="identifier"
                label="Henkilö- tai Y-tunnus"
                tooltipText="Esimerkiksi: 123456-123A"
                required
            />
            <TextInput
                name="email"
                label="Sähköpostiosoite"
            />
            <CheckboxInput
                name="non_disclosure"
                label="Turvakielto"
            />
            {
                // If valid identifier values are required and the identifier
                // is not one, show prompt for confirmation when submitting
                isInvalidSSNAllowed &&
                    !validateSocialSecurityNumber(formObject.getValues("identifier")) &&
                    isSubmitted && (
                        <p className="error-message">
                            "{formObject.getValues("identifier")}" ei ole oikea sosiaaliturvatunnus. Tallennetaanko
                            silti?
                        </p>
                    )
            }
            <div className="row row--buttons">
                <Button
                    onClick={cancelAction}
                    theme="black"
                    variant="secondary"
                >
                    Peruuta
                </Button>
                <SaveButton
                    isLoading={isLoading}
                    type="submit"
                    disabled={!isDirty || !isValid}
                />
            </div>
        </FormProviderForm>
    );
};

export default NewOwnerForm;
