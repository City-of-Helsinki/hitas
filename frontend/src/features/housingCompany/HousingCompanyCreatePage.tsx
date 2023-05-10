import {useEffect, useState} from "react";

import {Checkbox, Fieldset} from "hds-react";
import {useLocation, useNavigate} from "react-router-dom";
import {useImmer} from "use-immer";

import {
    useGetBuildingTypesQuery,
    useGetDevelopersQuery,
    useGetPostalCodesQuery,
    useGetPropertyManagersQuery,
    useSaveHousingCompanyMutation,
} from "../../app/services";
import {FormInputField, Heading, SaveButton, SaveDialogModal} from "../../common/components";
import {getHousingCompanyHitasTypeName, getHousingCompanyRegulationStatusName} from "../../common/localisation";
import {
    housingCompanyHitasTypes,
    housingCompanyRegulationStatus,
    ICode,
    IHousingCompanyDetails,
    IHousingCompanyWritable,
    IPostalCode,
    IPropertyManager,
} from "../../common/schemas";
import {hitasToast, validateBusinessId} from "../../common/utils";

interface IHousingCompanyLocationState {
    pathname: string;
    state: null | {housingCompany: IHousingCompanyDetails};
}

const HousingCompanyCreatePage = (): JSX.Element => {
    const navigate = useNavigate();
    const {pathname, state}: IHousingCompanyLocationState = useLocation();
    const isEditPage = pathname.split("/").at(-1) === "edit";

    const [isEndModalVisible, setIsEndModalVisible] = useState(false);

    const initialFormData: IHousingCompanyWritable =
        state === null || state?.housingCompany === undefined
            ? {
                  acquisition_price: 0,
                  address: {
                      postal_code: "",
                      street_address: "",
                  },
                  hitas_type: "new_hitas_1",
                  exclude_from_statistics: false,
                  regulation_status: "regulated",
                  building_type: {id: ""},
                  business_id: "",
                  developer: {id: ""},
                  name: {
                      display: "",
                      official: "",
                  },
                  notes: "",
                  primary_loan: undefined,
                  property_manager: null,
                  sales_price_catalogue_confirmation_date: null,
                  improvements: {
                      market_price_index: [],
                      construction_price_index: [],
                  },
              }
            : state.housingCompany;
    const [formData, setFormData] = useImmer<IHousingCompanyWritable>(initialFormData);
    const [saveHousingCompany, {data, error, isLoading}] = useSaveHousingCompanyMutation();

    const handleSaveButtonClicked = () => {
        saveHousingCompany({data: formData, id: state?.housingCompany.id});
    };

    // Navigate user directly to detail page of the just created Housing Company
    useEffect(() => {
        if (!isLoading && !error && data && data.id) {
            hitasToast("Asuntoyhtiö tallennettu onnistuneesti!");
            navigate(`/housing-companies/${data.id}`);
        } else if (error) {
            setIsEndModalVisible(true);
        }
    }, [isLoading, error, data, navigate]);

    // Redirect user to detail page if state is missing HousingCompany data and user is trying to edit the company
    useEffect(() => {
        if (isEditPage && state === null) navigate("..");
    }, [isEditPage, navigate, pathname, state]);

    const regulationStatusOptions = housingCompanyRegulationStatus.map((state) => {
        return {label: getHousingCompanyRegulationStatusName(state), value: state};
    });
    const hitasTypeOptions = housingCompanyHitasTypes.map((state) => {
        return {label: getHousingCompanyHitasTypeName(state), value: state};
    });

    return (
        <div className="view--create view--create-company">
            <Heading>
                <span>{state?.housingCompany ? state?.housingCompany.name.official : "Uusi yhtiö"}</span>
            </Heading>
            <div className="field-sets">
                <Fieldset heading="">
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
                    </div>
                    <div className="row">
                        <FormInputField
                            inputType="number"
                            unit="€"
                            fractionDigits={2}
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
                            fractionDigits={2}
                            label="Ensisijainen laina"
                            fieldPath="primary_loan"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <div className="row">
                        <FormInputField
                            inputType="select"
                            label="Sääntelyn tila"
                            fieldPath="regulation_status"
                            options={regulationStatusOptions}
                            defaultValue={{
                                label: getHousingCompanyRegulationStatusName(initialFormData.regulation_status),
                                value: initialFormData.regulation_status,
                            }}
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                            required
                        />
                        <FormInputField
                            inputType="select"
                            label="Hitas-tyyppi"
                            fieldPath="hitas_type"
                            options={hitasTypeOptions}
                            defaultValue={{
                                label: getHousingCompanyHitasTypeName(initialFormData.hitas_type),
                                value: initialFormData.hitas_type,
                            }}
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                            required
                        />
                    </div>
                    <div className="row">
                        <Checkbox
                            id="exclude_from_statistics-checkbox"
                            label="Ei-tilastoihin"
                            checked={formData.exclude_from_statistics}
                            onChange={(e) =>
                                setFormData((draft) => {
                                    draft.exclude_from_statistics = e.target.checked;
                                })
                            }
                            // tooltipText="Mikäli yhtiötä ei haluta mukaan '30v vertailuun',
                            // 'rajaneliöhinnan laskentaan' tai 'Toteutuneet kauppahinnat' tilastoihin."
                        />
                        <div />
                    </div>
                </Fieldset>
                <Fieldset heading="">
                    <div className="row">
                        <FormInputField
                            label="Y-Tunnus"
                            fieldPath="business_id"
                            validator={validateBusinessId}
                            tooltipText="Esimerkki arvo: '1234567-8'"
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
                    </div>
                    <div className="row">
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
                        <FormInputField
                            inputType="relatedModel"
                            label="Isännöitsijä"
                            fieldPath="property_manager.id"
                            placeholder={state?.housingCompany.property_manager?.name}
                            queryFunction={useGetPropertyManagersQuery}
                            relatedModelSearchField="name"
                            getRelatedModelLabel={(obj: IPropertyManager) => obj.name}
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
            </div>

            <SaveButton
                onClick={handleSaveButtonClicked}
                isLoading={isLoading}
            />
            <SaveDialogModal
                linkText="Yhtiön sivulle"
                baseURL="/housing-companies/"
                isVisible={isEndModalVisible}
                setIsVisible={setIsEndModalVisible}
                data={data}
                error={error}
                isLoading={isLoading}
            />
        </div>
    );
};

export default HousingCompanyCreatePage;
