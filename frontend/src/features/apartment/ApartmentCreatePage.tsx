import React from "react";

import {Button, Fieldset, IconSaveDisketteFill} from "hds-react";
import {DraftFunction, useImmer} from "use-immer";

import {useCreateApartmentMutation, useGetApartmentTypesQuery} from "../../app/services";
import {FormInputField} from "../../common/components";
import {IApartmentWritable, ICode} from "../../common/models";

function ApartmentCreateFields({
    formData,
    setFormData,
    error,
}: {
    formData: IApartmentWritable;
    setFormData: (arg: DraftFunction<IApartmentWritable> | IApartmentWritable) => void;
    error: unknown;
}) {
    return (
        <Fieldset
            heading="Asunnon tiedot"
            style={{
                display: "flex",
                flexDirection: "column",
                gridGap: "1em",
            }}
        >
            <FormInputField
                label="Katuosoite"
                fieldPath="address.street_address"
                required
                formData={formData}
                setFormData={setFormData}
                error={error}
            />
            <FormInputField
                label="Rappu"
                fieldPath="stair"
                required
                formData={formData}
                setFormData={setFormData}
                error={error}
            />
            <FormInputField
                inputType="number"
                label="Asunnon numero"
                fieldPath="apartment_number"
                required
                formData={formData}
                setFormData={setFormData}
                error={error}
            />
            <FormInputField
                inputType="number"
                label="Pinta-ala"
                fieldPath="surface_area"
                required
                formData={formData}
                setFormData={setFormData}
                error={error}
            />
            <FormInputField
                label="Asunto-osakeyhtiö"
                fieldPath="housing_company.name"
                required
                formData={formData}
                setFormData={setFormData}
                error={error}
            />
            <FormInputField
                inputType="relatedModel"
                label="Asuntotyyppi"
                fieldPath="apartment_type.id"
                queryFunction={useGetApartmentTypesQuery}
                relatedModelSearchField="value"
                getRelatedModelLabel={(obj: ICode) => obj.value}
                required
                formData={formData}
                setFormData={setFormData}
                error={error}
            />
            <FormInputField
                inputType="date"
                label="Valmistumispäivä"
                fieldPath="completion_date"
                required
                formData={formData}
                setFormData={setFormData}
                error={error}
            />
        </Fieldset>
    );
}

const ApartmentCreatePage = () => {
    // Create a new apartment
    const [formData, setFormData] = useImmer<IApartmentWritable>({
        state: "free",
        stair: "",
        address: {street_address: ""},
        housing_company: {name: ""},
        surface_area: 0,
        apartment_number: 0,
        apartment_type: {id: ""},
        apartment_building: "",
        ownerships: [""],
    });
    const [createApartment, {error}] = useCreateApartmentMutation();
    const handleSaveButtonClicked = () => {
        createApartment(formData);
    };
    return (
        <div className="view--set-apartment">
            <h1 className="main-heading">Uusi asunto</h1>
            <ApartmentCreateFields
                formData={formData}
                setFormData={setFormData}
                error={error}
            />
            <Button
                iconLeft={<IconSaveDisketteFill />}
                onClick={handleSaveButtonClicked}
                theme={"black"}
            >
                Tallenna
            </Button>
        </div>
    );
};

export default ApartmentCreatePage;
