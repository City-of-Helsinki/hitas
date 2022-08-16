import React from "react";

import {Button, Fieldset, IconSaveDisketteFill} from "hds-react";
import {useImmer} from "use-immer";

import {useCreateHousingCompanyMutation} from "../../app/services";
import {FormInputField} from "../../common/components";
import {HousingCompanyStates, IHousingCompanyWritable} from "../../common/models";
import {validateBusinessId} from "../../common/utils";

const HousingCompanyCreatePage = (): JSX.Element => {
    const [formData, setFormData] = useImmer<IHousingCompanyWritable>({
        acquisition_price: {initial: 10.0, realized: 10.0},
        address: {
            postal_code: "00100",
            street: "test-street-address-1",
        },
        building_type: {id: "f3a77a469fc34b45ba6dbaeebacd8a33"},
        business_id: "1234567-8",
        developer: {id: "06224336de274d87853afb950ba5ecc8"},
        financing_method: {id: "0a76cff05ecf4ebab050204c3477d1c9"},
        name: {
            display: "test-housing-company-1",
            official: "test-housing-company-1-as-oy",
        },
        notes: "This is a note.",
        primary_loan: 10.0,
        property_manager: {id: "2d9a7fac81e5426db3b33d6ad6ca9949"},
        state: "not_ready",
        sales_price_catalogue_confirmation_date: "2022-01-01",
    });
    const [createHousingCompany] = useCreateHousingCompanyMutation();

    const handleSaveButtonClicked = () => {
        createHousingCompany(formData);
    };

    return (
        <div className="company-details">
            <h1 className="main-heading">
                <span>Uusi asunto-yhtiö</span>
            </h1>
            <Fieldset
                heading="Perustiedot"
                style={{
                    display: "flex",
                    flexDirection: "column",
                    gridGap: "1em",
                }}
            >
                <FormInputField
                    label="Yhtiön hakunimi"
                    fieldPath="name.display"
                    required
                    formData={formData}
                    setFormData={setFormData}
                />
                <FormInputField
                    label="Yhtiön virallinen nimi"
                    fieldPath="name.official"
                    required
                    formData={formData}
                    setFormData={setFormData}
                />
                <FormInputField
                    label="Virallinen osoite"
                    fieldPath="address.street"
                    required
                    formData={formData}
                    setFormData={setFormData}
                />
                <FormInputField
                    inputType={"postalCode"}
                    label="Postinumero"
                    fieldPath="address.postal_code"
                    required
                    formData={formData}
                    setFormData={setFormData}
                />
                <FormInputField
                    inputType={"select"}
                    label="Tila"
                    fieldPath="state"
                    options={(() =>
                        HousingCompanyStates.map((state) => {
                            return {label: state};
                        }))()}
                    required
                    formData={formData}
                    setFormData={setFormData}
                />
                <FormInputField
                    inputType="money"
                    label="Hankinta-arvo"
                    fieldPath="acquisition_price.initial"
                    required
                    formData={formData}
                    setFormData={setFormData}
                />
                <FormInputField
                    inputType="money"
                    label="Toteutunut hankinta-arvo"
                    fieldPath="acquisition_price.realized"
                    required
                    formData={formData}
                    setFormData={setFormData}
                />
            </Fieldset>
            <Fieldset
                heading="Lisätiedot"
                style={{
                    display: "flex",
                    flexDirection: "column",
                    gridGap: "1em",
                }}
            >
                <FormInputField
                    label="Y-Tunnus"
                    fieldPath="business_id"
                    validator={validateBusinessId}
                    required
                    formData={formData}
                    setFormData={setFormData}
                />
                <FormInputField
                    inputType="date"
                    label="Myyntihintaluettelon vahvistamispäivä"
                    fieldPath="sales_price_catalogue_confirmation_date"
                    formData={formData}
                    setFormData={setFormData}
                />
                <FormInputField
                    inputType="money"
                    label="Ensisijainen laina"
                    fieldPath="primary_loan"
                    required
                    formData={formData}
                    setFormData={setFormData}
                />
                <FormInputField
                    label="Rahoitusmuoto"
                    fieldPath="financing_method.id"
                    required
                    formData={formData}
                    setFormData={setFormData}
                />
                <FormInputField
                    label="Talotyyppi"
                    fieldPath="building_type.id"
                    required
                    formData={formData}
                    setFormData={setFormData}
                />
                <FormInputField
                    label="Rakennuttaja"
                    fieldPath="developer.id"
                    required
                    formData={formData}
                    setFormData={setFormData}
                />
                <FormInputField
                    label="Isännöitsijä"
                    fieldPath="property_manager.id"
                    required
                    formData={formData}
                    setFormData={setFormData}
                />
                <FormInputField
                    label="Huomioitavaa"
                    fieldPath="notes"
                    formData={formData}
                    setFormData={setFormData}
                />
            </Fieldset>
            <Button
                iconLeft={<IconSaveDisketteFill />}
                onClick={handleSaveButtonClicked}
            >
                Tallenna
            </Button>
        </div>
    );
};

export default HousingCompanyCreatePage;
