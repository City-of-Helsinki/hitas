import React, {useEffect, useState} from "react";

import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {Button, Dialog, Fieldset, IconCheck, Tabs} from "hds-react";
import {useNavigate, useParams} from "react-router-dom";
import {useImmer} from "use-immer";

import {
    useGetApartmentDetailQuery,
    useGetHousingCompanyDetailQuery,
    useSaveApartmentMaximumPriceMutation,
} from "../../app/services";
import {
    FormInputField,
    ImprovementsTable,
    NavigateBackButton,
    QueryStateHandler,
    SaveButton,
} from "../../common/components";
import {
    IApartmentDetails,
    IApartmentMaximumPrice,
    IApartmentMaximumPriceWritable,
    IHousingCompanyDetails,
} from "../../common/models";
import {formatMoney, hitasToast} from "../../common/utils";

const CalculationRowPrice = ({label, calculation}) => {
    return (
        <div
            className={`confirmation-modal__calculation-row${
                calculation.maximum ? " confirmation-modal__calculation-row--maximum" : ""
            }`}
        >
            <label>{label}</label>
            <p>{formatMoney(calculation.maximum_price)}</p>
        </div>
    );
};

const MaximumPriceModalContent = ({
    calculation,
    apartment,
    setIsModalVisible,
}: {
    calculation: IApartmentMaximumPrice;
    apartment: IApartmentDetails;
    setIsModalVisible;
}) => {
    const navigate = useNavigate();
    const [confirmMaximumPrice, {data, error, isLoading}] = useSaveApartmentMaximumPriceMutation();
    const initiallyActiveTab = () => {
        switch (calculation.index) {
            case "market_price_index":
                return 0;
            case "construction_price_index":
                return 1;
            case "surface_area_price_ceiling":
                return 2;
            default:
                return 0;
        }
    };
    const handleConfirmButton = () => {
        confirmMaximumPrice({
            data: {confirm: true},
            id: calculation.id,
            apartmentId: apartment.id,
            housingCompanyId: apartment.links.housing_company.id,
        });
        setIsModalVisible(true);
    };
    useEffect(() => {
        if (!isLoading && !error && data && data.confirmed_at) {
            hitasToast("Enimmäishinta vahvistettu!");
            navigate(`/housing-companies/${apartment.links.housing_company.id}/apartments/${apartment.id}`);
        }
    }, [apartment, data, error, isLoading, navigate]);
    const BreakdownValue = ({label, value, unit = "€"}: {label: string; value?: number | string; unit?: string}) => (
        <div className="confirmation-modal__breakdown-row">
            <label>{label}</label>
            <p>{`${(value && value.toString()) || "0"} ${unit}`}</p>
        </div>
    );

    return (
        <>
            <Dialog.Content>
                <Tabs initiallyActiveTab={initiallyActiveTab()}>
                    <Tabs.TabList>
                        <Tabs.Tab>
                            <CalculationRowPrice
                                label="Markkinahintaindeksi"
                                calculation={calculation.calculations.market_price_index}
                            />
                        </Tabs.Tab>
                        <Tabs.Tab>
                            <CalculationRowPrice
                                label="Rakennuskustannusindeksi"
                                calculation={calculation.calculations.construction_price_index}
                            />
                        </Tabs.Tab>
                        <Tabs.Tab>
                            <CalculationRowPrice
                                label="Rajaneliöhinta"
                                calculation={calculation.calculations.surface_area_price_ceiling}
                            />
                        </Tabs.Tab>
                    </Tabs.TabList>
                    <Tabs.TabPanel className="confirmation-modal__breakdown">
                        <BreakdownValue
                            label="Hankinta-arvo"
                            value={calculation.calculations.market_price_index.calculation_variables.acquisition_price}
                        />
                        <BreakdownValue
                            label="+ Rakennusaikaiset lisä- ja muutostyöt"
                            value={
                                calculation.calculations.market_price_index.calculation_variables
                                    .additional_work_during_construction
                            }
                        />
                        <BreakdownValue
                            label="= Perushinta"
                            value={calculation.calculations.market_price_index.calculation_variables.basic_price}
                        />
                        <BreakdownValue
                            label="+ Indeksin muutos"
                            value={calculation.calculations.market_price_index.calculation_variables.index_adjustment}
                        />
                        <BreakdownValue
                            label="+ Huoneistokohtaiset parannukset"
                            value={
                                calculation.calculations.market_price_index.calculation_variables
                                    .housing_company_improvements?.summary.value
                            }
                        />
                        <BreakdownValue
                            label="+ Osuus yhtiön parannuksista"
                            value={
                                calculation.calculations.market_price_index.calculation_variables
                                    .housing_company_improvements?.summary.value_for_apartment
                            }
                        />
                        <BreakdownValue
                            label="= Osakkeiden velaton hinta"
                            value={calculation.calculations.market_price_index.calculation_variables.debt_free_price}
                        />
                        <BreakdownValue
                            label="+ Huoneistokohtaiset vähennykset"
                            value={calculation.calculations.market_price_index.calculation_variables.debt_free_price_m2}
                        />
                        <BreakdownValue
                            label={`- Osuus yhtiön lainoista (${calculation.calculations.construction_price_index.calculation_variables.calculation_date})`}
                            value={
                                calculation.calculations.market_price_index.calculation_variables
                                    .apartment_share_of_housing_company_loans
                            }
                        />
                        <BreakdownValue
                            label="= Enimmäismyyntihinta"
                            value={calculation.calculations.market_price_index.maximum_price}
                        />
                        <BreakdownValue
                            label="Velaton hinta euroa/m²"
                            value={calculation.calculations.market_price_index.calculation_variables.debt_free_price_m2}
                        />
                    </Tabs.TabPanel>
                    <Tabs.TabPanel className="confirmation-modal__breakdown">
                        <BreakdownValue
                            label="Hankinta-arvo"
                            value={
                                calculation.calculations.construction_price_index.calculation_variables
                                    .acquisition_price
                            }
                        />
                        <BreakdownValue
                            label="+ Rakennusaikaiset lisä- ja muutostyöt"
                            value={
                                calculation.calculations.construction_price_index.calculation_variables
                                    .additional_work_during_construction
                            }
                        />
                        <BreakdownValue
                            label="= Perushinta"
                            value={calculation.calculations.construction_price_index.calculation_variables.basic_price}
                        />
                        <BreakdownValue
                            label="+ Indeksin muutos"
                            value={
                                calculation.calculations.construction_price_index.calculation_variables.index_adjustment
                            }
                        />
                        <BreakdownValue
                            label="+ Huoneistokohtaiset parannukset"
                            value={
                                calculation.calculations.construction_price_index.calculation_variables
                                    .housing_company_improvements?.summary.value
                            }
                        />
                        <BreakdownValue
                            label="+ Osuus yhtiön parannuksista"
                            value={
                                calculation.calculations.construction_price_index.calculation_variables
                                    .housing_company_improvements?.summary.value_for_apartment
                            }
                        />
                        <BreakdownValue
                            label="= Osakkeiden velaton hinta"
                            value={
                                calculation.calculations.construction_price_index.calculation_variables.debt_free_price
                            }
                        />
                        <BreakdownValue
                            label="+ Huoneistokohtaiset vähennykset"
                            value={
                                calculation.calculations.construction_price_index.calculation_variables
                                    .debt_free_price_m2
                            }
                        />
                        <BreakdownValue
                            label={`- Osuus yhtiön lainoista (${calculation.calculations.construction_price_index.calculation_variables.calculation_date})`}
                            value={
                                calculation.calculations.construction_price_index.calculation_variables
                                    .apartment_share_of_housing_company_loans
                            }
                        />
                        <BreakdownValue
                            label="= Enimmäismyyntihinta"
                            value={calculation.calculations.construction_price_index.maximum_price}
                        />
                        <BreakdownValue
                            label="Velaton hinta euroa/m²"
                            value={
                                calculation.calculations.construction_price_index.calculation_variables
                                    .debt_free_price_m2
                            }
                        />
                    </Tabs.TabPanel>
                    <Tabs.TabPanel className="confirmation-modal__breakdown">
                        <BreakdownValue
                            label="Asunnon pinta-ala"
                            value={
                                calculation.calculations.surface_area_price_ceiling.calculation_variables.surface_area
                            }
                            unit="m²"
                        />
                        <BreakdownValue
                            label={`* Rajaneliöhinta (${calculation.calculations.surface_area_price_ceiling.calculation_variables.calculation_date})`}
                            value={
                                calculation.calculations.surface_area_price_ceiling.calculation_variables
                                    .calculation_date_value
                            }
                        />
                        <BreakdownValue
                            label={`- Osuus yhtiön lainoista (${calculation.calculations.construction_price_index.calculation_variables.calculation_date})`}
                            value={
                                calculation.calculations.market_price_index.calculation_variables
                                    .apartment_share_of_housing_company_loans
                            }
                        />
                        <BreakdownValue
                            label="= Enimmäishinta"
                            value={calculation.calculations.surface_area_price_ceiling.maximum_price}
                        />
                    </Tabs.TabPanel>
                </Tabs>
                <div className="valid-until">
                    <BreakdownValue
                        label="Vahvistettavan laskelman voimassaoloaika"
                        value={calculation.valid_until}
                        unit=""
                    />
                </div>
            </Dialog.Content>
            <Dialog.ActionButtons className="align-content-right">
                <Button
                    onClick={() => setIsModalVisible(false)}
                    variant="secondary"
                    theme="black"
                >
                    Peruuta
                </Button>
                <SaveButton
                    onClick={() => handleConfirmButton()}
                    isLoading={isLoading}
                />
            </Dialog.ActionButtons>
        </>
    );
};

const MaximumPriceModalError = ({error, setIsModalVisible}) => {
    const nonFieldError = ((error as FetchBaseQueryError)?.data as {message?: string})?.message || "";
    return (
        <>
            <Dialog.Content>
                <p>Virhe: {(error as FetchBaseQueryError)?.status}</p>
                <p>{nonFieldError}</p>
            </Dialog.Content>
            <Dialog.ActionButtons>
                <Button
                    onClick={() => setIsModalVisible(false)}
                    variant="secondary"
                    theme="black"
                >
                    Sulje
                </Button>
            </Dialog.ActionButtons>
        </>
    );
};

const LoadedApartmentMaxPrice = ({apartment}: {apartment: IApartmentDetails}): JSX.Element => {
    const [isModalVisible, setIsModalVisible] = useState<boolean>(false);
    const [formData, setFormData] = useImmer<IApartmentMaximumPriceWritable>({
        calculation_date: new Date().toISOString().split("T")[0], // Init with today's date in YYYY-MM format
        apartment_share_of_housing_company_loans: null,
        apartment_share_of_housing_company_loans_date: null,
        additional_info: "",
    });
    const {
        data: housingCompanyData,
        error: housingCompanyError,
        isLoading: isHousingCompanyLoading,
    } = useGetHousingCompanyDetailQuery(apartment.links.housing_company.id);
    const [saveMaximumPrice, {data, error, isLoading}] = useSaveApartmentMaximumPriceMutation();

    useEffect(() => {
        // Field errors, don't show modal as they are displayed on the fields instead
        if ((error as {data?: {fields: []}})?.data?.fields?.length) {
            setIsModalVisible(false);
        }
    }, [error]);

    const handleCalculateButton = () => {
        // Replace apartment_share_of_housing_company_loans `null` value with a zero (API expects an integer)
        const parsedFormData = {
            ...formData,
            apartment_share_of_housing_company_loans: formData.apartment_share_of_housing_company_loans || 0,
        };

        saveMaximumPrice({
            data: parsedFormData,
            id: undefined,
            apartmentId: apartment.id,
            housingCompanyId: apartment.links.housing_company.id,
        });

        setIsModalVisible(true);
    };

    return (
        <div className="view--set-apartment">
            <h1 className="main-heading">
                <div>
                    {apartment.address.street_address} - {apartment.address.stair}
                    {apartment.address.apartment_number} ({apartment.links.housing_company.display_name})
                </div>
            </h1>
            <div className="field-sets">
                <Fieldset heading="">
                    <h2 className="detail-list__heading">Laskentaan vaikuttavat asunnon tiedot</h2>
                    <div className="row">
                        <div>
                            <FormInputField
                                inputType="number"
                                unit="€"
                                label="Yhtiölainaosuus"
                                fieldPath="apartment_share_of_housing_company_loans"
                                formData={formData}
                                setFormData={setFormData}
                                error={error}
                            />
                            <FormInputField
                                inputType="date"
                                label="Yhtiölainaosuuden päivämäärä"
                                fieldPath="apartment_share_of_housing_company_loans_date"
                                formData={formData}
                                setFormData={setFormData}
                                error={error}
                                maxDate={new Date(new Date().setFullYear(new Date().getFullYear() + 1))}
                                tooltipText="Jos jätetään tyhjäksi, käytetään tämänhetkistä päivää."
                            />
                            <FormInputField
                                inputType="date"
                                label="Laskentapäivämäärä"
                                fieldPath="calculation_date"
                                formData={formData}
                                setFormData={setFormData}
                                error={error}
                                maxDate={new Date()}
                                tooltipText="Jos jätetään tyhjäksi, käytetään tämänhetkistä päivää."
                            />
                        </div>
                        <FormInputField
                            inputType="textArea"
                            label="Lisätieto"
                            fieldPath="additional_info"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <ImprovementsTable
                        data={apartment}
                        title="Laskentaan vaikuttavat asunnon parannukset"
                    />
                    <QueryStateHandler
                        data={housingCompanyData}
                        error={housingCompanyError}
                        isLoading={isHousingCompanyLoading}
                    >
                        <ImprovementsTable
                            data={housingCompanyData as IHousingCompanyDetails}
                            title="Yhtiökohtaiset parannukset"
                        />
                    </QueryStateHandler>
                    <div className="row row--buttons">
                        <NavigateBackButton />
                        <Button
                            theme="black"
                            onClick={handleCalculateButton}
                            iconLeft={<IconCheck />}
                        >
                            Laske
                        </Button>
                    </div>
                </Fieldset>
            </div>
            <Dialog
                id="maximum-price-confirmation-modal"
                closeButtonLabelText=""
                aria-labelledby=""
                isOpen={isModalVisible}
                close={() => setIsModalVisible(false)}
                boxShadow
            >
                <Dialog.Header
                    id="maximum-price-confirmation-modal-header"
                    title="Vahvistetaanko enimmäishintalaskelma?"
                />
                <QueryStateHandler
                    data={data}
                    error={error}
                    isLoading={isLoading}
                    errorComponent={
                        <MaximumPriceModalError
                            error={error}
                            setIsModalVisible={setIsModalVisible}
                        />
                    }
                >
                    <MaximumPriceModalContent
                        calculation={data as IApartmentMaximumPrice}
                        apartment={apartment}
                        setIsModalVisible={setIsModalVisible}
                    />
                </QueryStateHandler>
            </Dialog>
        </div>
    );
};

const ApartmentMaxPricePage = (): JSX.Element => {
    const params = useParams();
    const {data, error, isLoading} = useGetApartmentDetailQuery({
        housingCompanyId: params.housingCompanyId as string,
        apartmentId: params.apartmentId as string,
    });

    return (
        <div className="view--apartment view--apartment-details">
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <LoadedApartmentMaxPrice apartment={data as IApartmentDetails} />
            </QueryStateHandler>
        </div>
    );
};

export default ApartmentMaxPricePage;
