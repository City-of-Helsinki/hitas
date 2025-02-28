import React, {useContext, useRef, useState} from "react";

import {Fieldset, IconQuestionCircle, TextInput as HDSTextInput} from "hds-react";
import {useNavigate} from "react-router-dom";

import {zodResolver} from "@hookform/resolvers/zod";
import {useForm} from "react-hook-form";
import {z} from "zod";
import {GenericActionModal, NavigateBackButton, SaveButton, SaveDialogModal} from "../../common/components";
import {
    CheckboxInput,
    DateInput,
    FormProviderForm,
    NumberInput,
    RelatedModelInput,
    SaveFormButton,
    SelectInput,
    TextAreaInput,
    TextInput,
} from "../../common/components/forms";
import {getHousingCompanyHitasTypeName, getHousingCompanyRegulationStatusName} from "../../common/localisation";
import {
    housingCompanyHitasTypes,
    HousingCompanyWritableSchema,
    ICode,
    IHousingCompanyDetails,
    IHousingCompanyWritable,
    IPostalCode,
    IPropertyManager,
} from "../../common/schemas";
import {
    useGetBuildingTypesQuery,
    useGetDevelopersQuery,
    useGetPostalCodesQuery,
    useGetPropertyManagersQuery,
    useSaveHousingCompanyMutation,
} from "../../common/services";
import {formatDate, hdsToast, setAPIErrorsForFormFields, validateBusinessId} from "../../common/utils";
import {
    HousingCompanyViewContext,
    HousingCompanyViewContextProvider,
} from "./components/HousingCompanyViewContextProvider";

const regulationStatusOptions = [
    {label: getHousingCompanyRegulationStatusName("regulated"), value: "regulated"},
    {label: getHousingCompanyRegulationStatusName("released_by_hitas"), value: "released_by_hitas"},
    {label: getHousingCompanyRegulationStatusName("released_by_plot_department"), value: "released_by_plot_department"},
];

const hitasTypeOptions = housingCompanyHitasTypes.map((state) => {
    return {label: getHousingCompanyHitasTypeName(state), value: state};
});

const getInitialFormData = (housingCompany): IHousingCompanyWritable => {
    if (housingCompany) return housingCompany;

    return {
        acquisition_price: 0,
        address: {
            postal_code: "",
            street_address: "",
        },
        hitas_type: "new_hitas_1",
        exclude_from_statistics: false,
        regulation_status: "regulated",
        legacy_release_date: null,
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
    };
};

const LoadedHousingCompanyCreatePage = (): React.JSX.Element => {
    const navigate = useNavigate();
    const {housingCompany}: {housingCompany?: IHousingCompanyDetails} = useContext(HousingCompanyViewContext);

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isRegulationStatusModalOpen, setIsRegulationStatusModalOpen] = useState(false);

    const initialFormData: IHousingCompanyWritable = getInitialFormData(housingCompany);
    const formRef = useRef<HTMLFormElement>(null);
    const formObject = useForm<IHousingCompanyWritable>({
        defaultValues: initialFormData,
        mode: "onBlur",
        resolver: zodResolver(
            HousingCompanyWritableSchema.superRefine((data, ctx) => {
                // Price can be zero only if sale is excluded from statistics.
                if (!data.business_id) return;
                if (!validateBusinessId(data.business_id)) {
                    ctx.addIssue({
                        code: z.ZodIssueCode.custom,
                        path: ["business_id"],
                        message: "Y-Tunnuksen muoto on virheellinen",
                    });
                }
            })
        ),
    });

    const [
        saveHousingCompany,
        {data: housingCompanySaveData, error: housingCompanySaveError, isLoading: isHousingCompanySaveLoading},
    ] = useSaveHousingCompanyMutation();

    const onSubmit = (data) => {
        // Show a confirmation message if regulation status is changed before allowing the save
        if (
            housingCompany !== undefined &&
            housingCompany.regulation_status !== data.regulation_status &&
            !isRegulationStatusModalOpen
        ) {
            setIsRegulationStatusModalOpen(true);
            return;
        }

        saveHousingCompany({id: housingCompany?.id, data: data})
            .unwrap()
            .then((payload) => {
                hdsToast.success("Taloyhtiö tallennettu onnistuneesti!");
                navigate(`/housing-companies/${payload.id}`);
            })
            .catch((error) => {
                hdsToast.error("Virhe tallentaessa taloyhtiötä!");
                setIsModalOpen(true);
                setAPIErrorsForFormFields(formObject, error);
            });
    };

    const getReleaseDateDisplay = (housingCompany?: IHousingCompanyDetails) => {
        if (housingCompany) {
            if (housingCompany.legacy_release_date) {
                return "Vapautumispäivä korvattu";
            } else if (housingCompany.release_date) {
                return formatDate(housingCompany.release_date);
            }
        }
        return "Ei vapautumispäivää";
    };

    return (
        <>
            <FormProviderForm
                formObject={formObject}
                formRef={formRef}
                onSubmit={onSubmit}
            >
                <div className="field-sets">
                    <Fieldset heading="">
                        <div className="row">
                            <TextInput
                                label="Yhtiön virallinen nimi"
                                name="name.official"
                                required
                            />
                            <TextInput
                                label="Yhtiön hakunimi"
                                name="name.display"
                                required
                            />
                        </div>
                        <div className="row">
                            <TextInput
                                label="Katuosoite"
                                name="address.street_address"
                                required
                            />
                        </div>
                        <div className="row">
                            <RelatedModelInput
                                label="Postinumero"
                                name="address.postal_code"
                                queryFunction={useGetPostalCodesQuery}
                                relatedModelSearchField="value"
                                transform={(obj: string) => obj}
                                formatObjectForForm={(obj: IPostalCode) => obj.value}
                                required
                            />
                        </div>
                        <div className="row">
                            <NumberInput
                                label="Hankinta-arvo"
                                name="acquisition_price"
                                unit="€"
                                required
                            />
                            <NumberInput
                                label="Ensisijainen laina"
                                name="primary_loan"
                                unit="€"
                            />
                        </div>
                        <div className="row">
                            <SelectInput
                                label="Sääntelyn tila"
                                name="regulation_status"
                                options={regulationStatusOptions}
                                defaultValue={initialFormData.regulation_status}
                                setDirectValue
                                required
                            />
                            <SelectInput
                                label="Hitas-tyyppi"
                                name="hitas_type"
                                options={hitasTypeOptions}
                                defaultValue={initialFormData.hitas_type}
                                setDirectValue
                                required
                            />
                        </div>
                        <div className="row">
                            <HDSTextInput
                                id="release_date"
                                label="Laskennallinen vapautumispäivä"
                                readOnly={true}
                                defaultValue={getReleaseDateDisplay(housingCompany)}
                            />
                            <DateInput
                                label="Korvaava vapautumispäivä"
                                tooltipText="Tällä kentällä voi korvata automaattisesti lasketun vapautumispäivän. Oletuksena kentän voi jättää tyhjäksi."
                                name="legacy_release_date"
                            />
                        </div>
                        <div className="row">
                            <CheckboxInput
                                label="Ei-tilastoihin"
                                name="exclude_from_statistics"
                                tooltipText="Yhtiötä ei huomioida '30v vertailussa', 'rajaneliöhinnan laskennassa' tai 'Toteutuneet kauppahinnat' tilastoissa."
                            />
                            <div />
                        </div>
                    </Fieldset>
                    <Fieldset heading="">
                        <div className="row">
                            <TextInput
                                label="Y-Tunnus"
                                name="business_id"
                                tooltipText="Esimerkki arvo: '1234567-8'"
                            />
                            <DateInput
                                label="Myyntihintaluettelon vahvistamispäivä"
                                name="sales_price_catalogue_confirmation_date"
                            />
                        </div>
                        <div className="row">
                            <RelatedModelInput
                                label="Talotyyppi"
                                name="building_type"
                                queryFunction={useGetBuildingTypesQuery}
                                relatedModelSearchField="value"
                                transform={(obj: ICode) => obj.value}
                                required
                            />
                        </div>
                        <div className="row">
                            <RelatedModelInput
                                label="Rakennuttaja"
                                name="developer"
                                queryFunction={useGetDevelopersQuery}
                                relatedModelSearchField="value"
                                transform={(obj: ICode) => obj.value}
                                required
                            />
                            <RelatedModelInput
                                label="Isännöitsijä"
                                name="property_manager"
                                queryFunction={useGetPropertyManagersQuery}
                                relatedModelSearchField="name"
                                transform={(obj: IPropertyManager) => obj.name}
                            />
                        </div>
                        <TextAreaInput
                            label="Huomioitavaa"
                            name="notes"
                        />
                    </Fieldset>
                </div>

                <div className="row row--buttons">
                    <NavigateBackButton />
                    <SaveButton
                        type="submit"
                        isLoading={isHousingCompanySaveLoading}
                    />
                </div>
            </FormProviderForm>

            <GenericActionModal
                title="Yhtiön sääntelyn tilan muutos"
                modalIcon={<IconQuestionCircle />}
                isModalOpen={isRegulationStatusModalOpen}
                closeModal={() => setIsRegulationStatusModalOpen(false)}
                confirmButton={
                    <SaveFormButton
                        formRef={formRef}
                        isLoading={isHousingCompanySaveLoading}
                    />
                }
            >
                <p>
                    Olet muuttamassa yhtiön <b>{housingCompany?.name.display}</b> sääntelyn tilaa.
                </p>
                <p>
                    Vahvista, että yhtiö on tarkoitus asettaa tilaan '
                    <b>{getHousingCompanyRegulationStatusName(formObject.getValues("regulation_status"))}</b>'.
                </p>
            </GenericActionModal>

            <SaveDialogModal
                linkText="Yhtiön sivulle"
                baseURL="/housing-companies/"
                isVisible={isModalOpen}
                setIsVisible={setIsModalOpen}
                data={housingCompanySaveData}
                error={housingCompanySaveError}
                isLoading={isHousingCompanySaveLoading}
            />
        </>
    );
};

const HousingCompanyCreatePage = (): React.JSX.Element => {
    return (
        <HousingCompanyViewContextProvider viewClassName="view--create view--create-company">
            <LoadedHousingCompanyCreatePage />
        </HousingCompanyViewContextProvider>
    );
};

export default HousingCompanyCreatePage;
