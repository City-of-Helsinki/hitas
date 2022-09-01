import React from "react";

import {Button, IconSaveDisketteFill} from "hds-react";
import {DraftFunction, useImmer} from "use-immer";

import {useCreateApartmentMutation} from "../../app/services";
import {FormInputField} from "../../common/components";
import {IApartmentWritable} from "../../common/models";

function SetApartmentFields({
    formData,
    setFormData,
    error,
}: {
    formData: IApartmentWritable;
    setFormData: (arg: DraftFunction<IApartmentWritable> | IApartmentWritable) => void;
    error: any;
}) {
    return (
        <>
            <FormInputField
                label="Katuosoite"
                fieldPath="address.street_address"
                required
                formData={formData}
                setFormData={setFormData}
                error={error}
            />
            <FormInputField
                label="Asunnon numero"
                fieldPath="apartment_number"
                required
                formData={formData}
                setFormData={setFormData}
                error={error}
            />
        </>
    );
}

function SaveButton(props: {onClick: () => void}) {
    return (
        <Button
            iconLeft={<IconSaveDisketteFill />}
            onClick={props.onClick}
            theme={"black"}
        >
            Tallenna
        </Button>
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
        completion_date: new Date(),
    });
    const [setApartment, {error}] = useCreateApartmentMutation();
    const handleSaveButtonClicked = () => {
        setApartment(formData);
    };
    return (
        <div className="view--set-apartment">
            <h1 className="main-heading">Uusi asunto</h1>
            <SetApartmentFields
                formData={formData}
                setFormData={setFormData}
                error={error}
            />
            <SaveButton onClick={handleSaveButtonClicked} />
        </div>
    );
};

export default ApartmentCreatePage;
