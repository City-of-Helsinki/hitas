import React, {useState} from "react";

import {Button, Fieldset, IconSaveDisketteFill} from "hds-react";
import {useImmer} from "use-immer";

import {
    useCreateApartmentMutation,
    useGetApartmentTypesQuery,
    useGetHousingCompaniesQuery, // useGetPersonsQuery,
} from "../../app/services";
import {FormInputField, SaveDialogModal} from "../../common/components";
import {ApartmentState, ApartmentStates, IApartmentWritable, ICode, IOwnership} from "../../common/models";

const ApartmentCreatePage = () => {
    // eslint-disable-next-line no-unused-vars
    const [currentOwnerships, setCurrentOwnerships] = useState(0);
    const [isEndModalVisible, setIsEndModalVisible] = useState(false);
    const blankOwnership = {owner: {id: ""}, percentage: 0};
    const blankForm = {
        state: "free" as ApartmentState,
        apartment_type: {id: ""},
        surface_area: 0,
        share_number_start: 0,
        share_number_end: 0,
        address: {
            street_address: "",
            postal_code: "",
            apartment_number: 0,
            floor: "",
            stair: "",
        },
        apartment_number: 0,
        floor: 0,
        stair: "",
        completion_date: new Date(),
        debt_free_purchase_price: 0,
        purchase_price: 0,
        acquisition_price: 0,
        primary_loan_amount: 0,
        loans_during_construction: 0,
        interest_during_construction: 0,
        building: {id: ""},
        real_estate: {id: ""},
        housing_company: {name: ""},
        ownerships: [blankOwnership],
        notes: "",
    };
    const [formData, setFormData] = useImmer<IApartmentWritable>(blankForm as IApartmentWritable);
    const [formOwnerships, setFormOwnerships] = useImmer([blankOwnership] as Array<IOwnership>);
    const [createApartment, {data, error, isLoading}] = useCreateApartmentMutation();
    const Ownership = (ownership) => (
        <li className="ownership-item">
            <FormInputField
                label="Omistaja"
                fieldPath="owner"
                required
                formData={formOwnerships}
                setFormData={setFormOwnerships}
                error={error}
            />
            <FormInputField
                inputType="number"
                label="Omistusprosentti"
                fieldPath={`percentage`}
                required
                formData={formOwnerships}
                setFormData={setFormOwnerships}
                error={error}
            />
        </li>
    );
    const handleSaveButtonClicked = () => {
        try {
            createApartment(formData);
        } catch (error) {
            console.error(error);
        } finally {
            console.log("finished");
            setIsEndModalVisible(true);
        }
    };
    const addOwner = () => {
        setCurrentOwnerships(() => {
            return formOwnerships.length + 1;
        });
        console.log(formData.ownerships);
    };
    return (
        <div className="view--create view--set-apartment">
            <h1 className="main-heading">Uusi asunto</h1>
            <div className="field-sets">
                <Fieldset
                    heading="Asunnon tiedot"
                    style={{
                        display: "flex",
                        flexDirection: "column",
                        gridGap: "1em",
                    }}
                >
                    <FormInputField
                        inputType={"select"}
                        label="Tila"
                        fieldPath="state"
                        options={(() =>
                            ApartmentStates.map((state) => {
                                return {label: state};
                            }))()}
                        required
                        formData={formData}
                        setFormData={setFormData}
                        error={error}
                    />
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
                        label="Kerros"
                        fieldPath="floor"
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
                        inputType="relatedModel"
                        label="Asunto-osakeyhtiö"
                        field="id"
                        fieldPath="housing_company.id"
                        queryFunction={useGetHousingCompaniesQuery}
                        relatedModelSearchField="value"
                        getRelatedModelLabel={(obj: ICode) => obj.value}
                        required
                        formData={formData}
                        setFormData={setFormData}
                        error={error}
                    />
                    <FormInputField
                        inputType="relatedModel"
                        label="Asuntotyyppi"
                        field="id"
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
                <Fieldset heading="Hinnat, lainat ja omistajuudet">
                    <FormInputField
                        inputType="number"
                        unit="€"
                        label="Velaton ostohinta"
                        fieldPath="debt_free_purchase_price"
                        required
                        formData={formData}
                        setFormData={setFormData}
                        error={error}
                    />
                    <FormInputField
                        inputType="number"
                        unit="€"
                        label="Ostohinta"
                        fieldPath="purchase_price"
                        required
                        formData={formData}
                        setFormData={setFormData}
                        error={error}
                    />
                    <FormInputField
                        inputType="number"
                        unit="€"
                        label="Hankinta-arvo"
                        fieldPath="acquisition_price"
                        required
                        formData={formData}
                        setFormData={setFormData}
                        error={error}
                    />
                    <FormInputField
                        inputType="number"
                        unit="€"
                        label="Ensisijainen laina"
                        fieldPath="primary_loan_amount"
                        required
                        formData={formData}
                        setFormData={setFormData}
                        error={error}
                    />
                    <FormInputField
                        inputType="number"
                        unit="€"
                        label="Rakennusaikaiset laina"
                        fieldPath="loans_during_construction"
                        required
                        formData={formData}
                        setFormData={setFormData}
                        error={error}
                    />
                    <FormInputField
                        inputType="number"
                        unit="€"
                        label="Rakennusaikaiset korot"
                        fieldPath="interest_during_construction"
                        required
                        formData={formData}
                        setFormData={setFormData}
                        error={error}
                    />
                    <h4>Omistajuudet</h4>
                    <ul className="ownerships-list">
                        {formOwnerships.map((ownership, num) => (
                            <Ownership
                                key={num}
                                ownership={ownership}
                            />
                        ))}
                    </ul>
                    <Button
                        onClick={addOwner}
                        variant="secondary"
                        theme="black"
                    >
                        Lisää omistajuus
                    </Button>
                </Fieldset>
            </div>
            <Button
                iconLeft={<IconSaveDisketteFill />}
                onClick={handleSaveButtonClicked}
                theme={"black"}
            >
                Tallenna
            </Button>
            {/*
             Save attempt modal dialog
             */}
            <SaveDialogModal
                data={data}
                error={error}
                isLoading={isLoading}
                isVisible={isEndModalVisible}
                setIsVisible={setIsEndModalVisible}
            />
        </div>
    );
};

export default ApartmentCreatePage;
