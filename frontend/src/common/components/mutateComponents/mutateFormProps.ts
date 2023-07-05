import {useSaveDeveloperMutation, useSavePropertyManagerMutation} from "../../../app/services";
import {DeveloperSchema, PropertyManagerSchema} from "../../schemas";

export const propertyManagerMutateFormProps = {
    formObjectSchema: PropertyManagerSchema,
    useSaveMutation: useSavePropertyManagerMutation,
    successMessage: "Isännöitsijän tiedot tallennettu onnistuneesti!",
    errorMessage: "Virhe isännöitsijän tietojen tallentamisessa!",
    notModifiedMessage: "Ei muutoksia isännöitsijän tiedoissa.",
    formFieldsWithTitles: {name: "Nimi", email: "Sähköpostiosoite"},
    requiredFields: ["name"],
};

export const developerMutateFormProps = {
    formObjectSchema: DeveloperSchema,
    useSaveMutation: useSaveDeveloperMutation,
    successMessage: "Rakennuttajan tiedot tallennettu onnistuneesti!",
    errorMessage: "Virhe rakennuttajan tietojen tallentamisessa!",
    notModifiedMessage: "Ei muutoksia rakennuttajan tiedoissa.",
    formFieldsWithTitles: {value: "Nimi", description: "Kuvaus"},
    requiredFields: ["value", "description"],
};
