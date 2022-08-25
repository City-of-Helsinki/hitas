import React from "react";

import {Button, Fieldset, IconSaveDisketteFill} from "hds-react";
import {useImmer} from "use-immer";

import {
    useCreateHousingCompanyMutation,
    useGetBuildingTypesQuery,
    useGetDevelopersQuery,
    useGetFinancingMethodsQuery,
    useGetPropertyManagersQuery,
} from "../../app/services";
import {FormInputField} from "../../common/components";
import {HousingCompanyStates, ICode, IHousingCompanyWritable, IPropertyManager} from "../../common/models";
import {validateBusinessId} from "../../common/utils";

const HousingCompanyCreatePage = (): JSX.Element => {
    const [formData, setFormData] = useImmer<IHousingCompanyWritable>({
        acquisition_price: {initial: null, realized: null},
        address: {
            postal_code: "",
            street_address: "",
        },
        building_type: {id: ""},
        business_id: "",
        developer: {id: ""},
        financing_method: {id: ""},
        name: {
            display: "",
            official: "",
        },
        notes: "",
        primary_loan: null,
        property_manager: {id: ""},
        state: "not_ready",
        sales_price_catalogue_confirmation_date: "",
    });
    const [createHousingCompany, {error}] = useCreateHousingCompanyMutation();

    const handleSaveButtonClicked = () => {
        createHousingCompany(formData);
    };

    console.log(formData.sales_price_catalogue_confirmation_date);

    return (
        <div className="view--create-company">
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
                    error={error}
                />
                <FormInputField
                    label="Yhtiön virallinen nimi"
                    fieldPath="name.official"
                    required
                    formData={formData}
                    setFormData={setFormData}
                    error={error}
                />
                <FormInputField
                    label="Virallinen osoite"
                    fieldPath="address.street_address"
                    required
                    formData={formData}
                    setFormData={setFormData}
                    error={error}
                />
                <FormInputField
                    inputType={"postalCode"}
                    label="Postinumero"
                    fieldPath="address.postal_code"
                    required
                    formData={formData}
                    setFormData={setFormData}
                    error={error}
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
                    error={error}
                />
                <FormInputField
                    inputType="money"
                    label="Hankinta-arvo"
                    fieldPath="acquisition_price.initial"
                    required
                    formData={formData}
                    setFormData={setFormData}
                    error={error}
                />
                <FormInputField
                    inputType="money"
                    label="Toteutunut hankinta-arvo"
                    fieldPath="acquisition_price.realized"
                    formData={formData}
                    setFormData={setFormData}
                    error={error}
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
                    tooltipText={"Esimerkki arvo: '1234567-8'"}
                    required
                    formData={formData}
                    setFormData={setFormData}
                    error={error}
                />
                <FormInputField
                    inputType="date"
                    label="Myyntihintaluettelon vahvistamispäivä"
                    fieldPath="sales_price_catalogue_confirmation_date"
                    formData={formData}
                    setFormData={setFormData}
                    error={error}
                />
                <FormInputField
                    inputType="money"
                    label="Ensisijainen laina"
                    fieldPath="primary_loan"
                    required
                    formData={formData}
                    setFormData={setFormData}
                    error={error}
                />
                <FormInputField
                    inputType="relatedModel"
                    label="Rahoitusmuoto"
                    fieldPath="financing_method.id"
                    queryFunction={useGetFinancingMethodsQuery}
                    relatedModelSearchField="value"
                    getRelatedModelLabel={(obj: ICode) => obj.value}
                    required
                    formData={formData}
                    setFormData={setFormData}
                    error={error}
                />
                <FormInputField
                    inputType="relatedModel"
                    label="Talotyyppi"
                    fieldPath="building_type.id"
                    queryFunction={useGetBuildingTypesQuery}
                    relatedModelSearchField="value"
                    getRelatedModelLabel={(obj: ICode) => obj.value}
                    required
                    formData={formData}
                    setFormData={setFormData}
                    error={error}
                />
                <FormInputField
                    inputType="relatedModel"
                    label="Rakennuttaja"
                    fieldPath="developer.id"
                    queryFunction={useGetDevelopersQuery}
                    relatedModelSearchField="value"
                    getRelatedModelLabel={(obj: ICode) => obj.value}
                    required
                    formData={formData}
                    setFormData={setFormData}
                    error={error}
                />
                <FormInputField
                    inputType="relatedModel"
                    label="Isännöitsijä"
                    fieldPath="property_manager.id"
                    queryFunction={useGetPropertyManagersQuery}
                    relatedModelSearchField="name"
                    getRelatedModelLabel={(obj: IPropertyManager) => obj.name}
                    required
                    formData={formData}
                    setFormData={setFormData}
                    error={error}
                />
                <FormInputField
                    inputType="textArea"
                    label="Huomioitavaa"
                    fieldPath="notes"
                    formData={formData}
                    setFormData={setFormData}
                    error={error}
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
