import React, {useState} from "react";

import {Button, Fieldset, IconSaveDisketteFill} from "hds-react";
import {useImmer} from "use-immer";

import {
    useCreateHousingCompanyMutation,
    useGetBuildingTypesQuery,
    useGetDevelopersQuery,
    useGetFinancingMethodsQuery,
    useGetPostalCodesQuery,
    useGetPropertyManagersQuery,
} from "../../app/services";
import {FormInputField, SaveDialogModal} from "../../common/components";
import {HousingCompanyStates, ICode, IHousingCompanyWritable, IPostalCode, IPropertyManager} from "../../common/models";
import {validateBusinessId} from "../../common/utils";

const HousingCompanyCreatePage = (): JSX.Element => {
    const [isEndModalVisible, setIsEndModalVisible] = useState(false);
    const blankForm = {
        acquisition_price: {
            initial: null,
            realized: null,
        },
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
        sales_price_catalogue_confirmation_date: null,
    };
    const [formData, setFormData] = useImmer<IHousingCompanyWritable>(blankForm as IHousingCompanyWritable);
    const [createHousingCompany, {data, error, isLoading}] = useCreateHousingCompanyMutation();

    const handleSaveButtonClicked = () => {
        createHousingCompany(formData);
        setIsEndModalVisible(true);
    };

    return (
        <div className="view--create view--create-company">
            <h1 className="main-heading">
                <span>Uusi asunto-yhtiö</span>
            </h1>
            <div className="field-sets">
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
                        inputType="relatedModel"
                        label="Postinumero"
                        field="value"
                        fieldPath="address.postal_code"
                        queryFunction={useGetPostalCodesQuery}
                        relatedModelSearchField="value"
                        getRelatedModelLabel={(obj: IPostalCode) => obj.value}
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
                        inputType="number"
                        unit="€"
                        label="Hankinta-arvo"
                        fieldPath="acquisition_price.initial"
                        required
                        formData={formData}
                        setFormData={setFormData}
                        error={error}
                    />
                    <FormInputField
                        inputType="number"
                        unit="€"
                        label="Toteutunut hankinta-arvo"
                        fieldPath="acquisition_price.realized"
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
                        inputType="number"
                        unit="€"
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
                        field="id"
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
                        field="id"
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
                        field="id"
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
                        field="id"
                        fieldPath="property_manager.id"
                        queryFunction={useGetPropertyManagersQuery}
                        relatedModelSearchField="name"
                        getRelatedModelLabel={(obj: IPropertyManager) => obj.name}
                        required
                        formData={formData}
                        setFormData={setFormData}
                        error={error}
                    />
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

export default HousingCompanyCreatePage;
