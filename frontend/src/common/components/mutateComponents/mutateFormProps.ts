import {DeveloperSchema, PropertyManagerSchema} from "../../schemas";
import {
    useSaveDeveloperMutation,
    useSavePropertyManagerMutation,
    useDeletePropertyManagerMutation,
} from "../../services";

export const propertyManagerMutateFormProps = {
    formObjectSchema: PropertyManagerSchema,
    useSaveMutation: useSavePropertyManagerMutation,
    successMessage: "Isännöitsijän tiedot tallennettu onnistuneesti!",
    errorMessage: "Virhe isännöitsijän tietojen tallentamisessa!",
    notModifiedMessage: "Ei muutoksia isännöitsijän tiedoissa.",
    formFieldsWithTitles: {name: "Nimi", email: "Sähköpostiosoite"},
    requiredFields: ["name"],
    deleteProps: {
        useDeleteMutation: useDeletePropertyManagerMutation,
        modalText: (obj) => `Haluatko varmasti poistaa isännöitsijän ${obj.name}${obj.email ? ` (${obj.email})` : ""}?`,
        successText: "Isännöitsijä poistettu",
        successToastText: "Isännöitsijä poistettu onnistuneesti!",
        errorToastText: "Virhe isännöitsijän poistamisessa!",
    },
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
