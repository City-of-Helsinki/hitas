import React, {useState} from "react";

import {Button, Fieldset, IconSaveDisketteFill} from "hds-react";
import {useLocation} from "react-router";
import {useImmer} from "use-immer";

import {
    useGetBuildingTypesQuery,
    useGetDevelopersQuery,
    useGetFinancingMethodsQuery,
    useGetPostalCodesQuery,
    useGetPropertyManagersQuery,
    useSaveHousingCompanyMutation,
} from "../../app/services";
import {FormInputField, SaveDialogModal} from "../../common/components";
import {HousingCompanyStates, ICode, IHousingCompanyWritable, IPostalCode, IPropertyManager} from "../../common/models";
import {validateBusinessId} from "../../common/utils";

const getHousingCompanyStateName = (state) => {
    switch (state) {
        case "not_ready":
            return "Ei valmis";
        case "lt_30_years":
            return "Alle 30-vuotta";
        case "gt_30_years_not_free":
            return "Yli 30-vuotta, ei vapautunut";
        case "gt_30_years_free":
            return "Yli 30-vuotta, vapautunut";
        case "gt_30_years_plot_department_notification":
            return "Yli 30-vuotta, vapautunut tonttiosaston ilmoitus";
        case "half_hitas":
            return "Puoli-hitas";
        case "ready_no_statistics":
            return "Valmis, ei tilastoihin";
        default:
            return "VIRHE";
    }
};

const HousingCompanyCreatePage = (): JSX.Element => {
    const {state} = useLocation();
    const [isEndModalVisible, setIsEndModalVisible] = useState(false);

    const initialFormData: IHousingCompanyWritable =
        state?.housingCompany === undefined
            ? {
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
                  improvements: {
                      market_price_index: [],
                      construction_price_index: [],
                  },
              }
            : state.housingCompany;
    const [formData, setFormData] = useImmer<IHousingCompanyWritable>(initialFormData);
    const [createHousingCompany, {data, error, isLoading}] = useSaveHousingCompanyMutation();

    const handleSaveButtonClicked = () => {
        createHousingCompany({data: formData, id: state?.housingCompany.id});
        setIsEndModalVisible(true);
    };
    const stateOptions = HousingCompanyStates.map((state) => {
        return {label: getHousingCompanyStateName(state), value: state};
    });
    return (
        <div className="view--create view--create-company">
            <h1 className="main-heading">
                <span>Uusi yhtiö</span>
            </h1>
            <div className="field-sets">
                <Fieldset heading="Perustiedot">
                    <div className="row">
                        <FormInputField
                            label="Yhtiön virallinen nimi"
                            fieldPath="name.official"
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                        <FormInputField
                            label="Yhtiön hakunimi"
                            fieldPath="name.display"
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <div className="row">
                        <FormInputField
                            label="Katuosoite"
                            fieldPath="address.street_address"
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <div className="row">
                        <FormInputField
                            inputType="relatedModel"
                            label="Postinumero"
                            requestedField="value"
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
                            options={stateOptions}
                            defaultValue={{label: "Ei valmis", value: "not_ready"}}
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <div className="row">
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
                    </div>
                    <FormInputField
                        inputType="textArea"
                        label="Huomioitavaa"
                        fieldPath="notes"
                        formData={formData}
                        setFormData={setFormData}
                        error={error}
                    />
                </Fieldset>
                <Fieldset heading="Lisätiedot">
                    <div className="row">
                        <FormInputField
                            label="Y-Tunnus"
                            fieldPath="business_id"
                            validator={validateBusinessId}
                            tooltipText={"Esimerkki arvo: '1234567-8'"}
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
                    </div>
                    <div className="row">
                        <FormInputField
                            inputType="number"
                            unit="€"
                            label="Ensisijainen laina"
                            fieldPath="primary_loan"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                        <FormInputField
                            inputType="relatedModel"
                            label="Rahoitusmuoto"
                            fieldPath="financing_method.id"
                            placeholder={state?.housingCompany.financing_method.value}
                            queryFunction={useGetFinancingMethodsQuery}
                            relatedModelSearchField="value"
                            getRelatedModelLabel={(obj: ICode) => obj.value}
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <div className="row">
                        <FormInputField
                            inputType="relatedModel"
                            label="Talotyyppi"
                            fieldPath="building_type.id"
                            placeholder={state?.housingCompany.building_type.value}
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
                            placeholder={state?.housingCompany.developer.value}
                            queryFunction={useGetDevelopersQuery}
                            relatedModelSearchField="value"
                            getRelatedModelLabel={(obj: ICode) => obj.value}
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <FormInputField
                        inputType="relatedModel"
                        label="Isännöitsijä"
                        fieldPath="property_manager.id"
                        placeholder={state?.housingCompany.property_manager.name}
                        queryFunction={useGetPropertyManagersQuery}
                        relatedModelSearchField="name"
                        getRelatedModelLabel={(obj: IPropertyManager) => obj.name}
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
                baseURL="/housing-companies/"
                itemName="Yhtiön"
                isLoading={isLoading}
                isVisible={isEndModalVisible}
                setIsVisible={setIsEndModalVisible}
            />
        </div>
    );
};

export default HousingCompanyCreatePage;
