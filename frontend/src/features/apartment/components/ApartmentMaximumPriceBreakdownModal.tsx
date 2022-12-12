import React, {useEffect} from "react";

import {Button, Dialog, Tabs} from "hds-react";
import {useNavigate} from "react-router-dom";

import {useSaveApartmentMaximumPriceMutation} from "../../../app/services";
import {SaveButton} from "../../../common/components";
import {
    IApartmentDetails,
    IApartmentMaximumPrice,
    IIndexCalculation2011Onwards,
    IIndexCalculationConstructionPriceIndexBefore2011,
    IIndexCalculationMarketPriceIndexBefore2011,
    SurfaceAreaPriceCeilingCalculation,
} from "../../../common/models";
import {formatDate, formatMoney, hitasToast} from "../../../common/utils";

const BreakdownTabButton = ({label, calculation}) => {
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

const BreakdownValue = ({label, value, unit = "€"}: {label: string; value?: number | string; unit?: string}) => (
    <div className="confirmation-modal__breakdown-row">
        <label>{label}</label>
        <p>{`${(value && value.toString()) || "0"} ${unit}`}</p>
    </div>
);

const Breakdown2011Onwards = ({calculation}: {calculation: IIndexCalculation2011Onwards}) => {
    return (
        <>
            <BreakdownValue
                label="Hankinta-arvo"
                value={calculation.calculation_variables.acquisition_price}
            />
            {calculation.calculation_variables.additional_work_during_construction ? (
                <BreakdownValue
                    label="+ Rakennusaikaiset lisä- ja muutostyöt"
                    value={calculation.calculation_variables.additional_work_during_construction}
                />
            ) : null}
            <BreakdownValue
                label="= Perushinta"
                value={calculation.calculation_variables.basic_price}
            />
            <BreakdownValue
                label="+ Indeksin muutos"
                value={calculation.calculation_variables.index_adjustment}
            />
            <BreakdownValue
                label="+ Osuus yhtiön parannuksista"
                value={calculation.calculation_variables.housing_company_improvements?.summary.value_for_apartment}
            />
            <BreakdownValue
                label="= Osakkeiden velaton hinta"
                value={calculation.calculation_variables.debt_free_price}
            />
            <BreakdownValue
                label={`- Osuus yhtiön lainoista (${formatDate(
                    calculation.calculation_variables.apartment_share_of_housing_company_loans_date
                )})`}
                value={calculation.calculation_variables.apartment_share_of_housing_company_loans}
            />
            <BreakdownValue
                label="= Enimmäismyyntihinta"
                value={calculation.maximum_price}
            />
            <BreakdownValue
                label="Velaton hinta euroa/m²"
                value={calculation.calculation_variables.debt_free_price_m2}
            />
        </>
    );
};

const MarketPricePre2011Breakdown = ({calculation}: {calculation: IIndexCalculationMarketPriceIndexBefore2011}) => {
    return (
        <>
            <BreakdownValue
                label="Hankinta-arvo"
                value={calculation.calculation_variables.acquisition_price}
            />
            <BreakdownValue
                label="+ Rakennusaikaiset korot (TODO %)"
                value={calculation.calculation_variables.interest_during_construction}
            />
            <BreakdownValue
                label="= Perushinta"
                value={calculation.calculation_variables.basic_price}
            />
            <BreakdownValue
                label="+ Indeksin muutos"
                value={calculation.calculation_variables.index_adjustment}
            />
            <BreakdownValue
                label="+ Huoneistokohtaiset parannukset"
                value={calculation.calculation_variables.apartment_improvements.summary.accepted_value}
            />
            <BreakdownValue
                label="+ Osuus yhtiön parannuksista"
                value={calculation.calculation_variables.housing_company_improvements.summary.accepted_value}
            />
            <BreakdownValue
                label="= Osakkeiden velaton hinta"
                value={calculation.calculation_variables.debt_free_price}
            />
            <BreakdownValue
                label={`- Osuus yhtiön lainoista (${formatDate(
                    calculation.calculation_variables.apartment_share_of_housing_company_loans_date
                )})`}
                value={calculation.calculation_variables.apartment_share_of_housing_company_loans}
            />
            <BreakdownValue
                label="= Enimmäismyyntihinta"
                value={calculation.maximum_price}
            />
            <BreakdownValue
                label="Velaton hinta euroa/m²"
                value={calculation.calculation_variables.debt_free_price_m2}
            />
        </>
    );
};

const ConstructionPricePre2011Breakdown = ({
    calculation,
}: {
    calculation: IIndexCalculationConstructionPriceIndexBefore2011;
}) => {
    return (
        <>
            <BreakdownValue
                label="Yhtiön tarkistettu hankinta-arvo"
                value={calculation.calculation_variables.housing_company_acquisition_price}
            />
            <BreakdownValue
                label="+ Kiinteistön parannukset"
                value={calculation.calculation_variables.housing_company_improvements.summary.value}
            />
            <BreakdownValue
                label="= Yhtiön varat yhteensä"
                value={calculation.calculation_variables.housing_company_assets}
            />
            <BreakdownValue
                label="Osakkeiden osuus"
                value={calculation.calculation_variables.apartment_share_of_housing_company_assets}
            />
            <BreakdownValue
                label="+ Rakennusaikaiset korot (TODO %)"
                value={calculation.calculation_variables.interest_during_construction}
            />
            <BreakdownValue
                label="+ Huoneistokohtaiset parannukset"
                value={calculation.calculation_variables.apartment_improvements.summary.value_for_apartment}
            />
            <BreakdownValue
                label="= Osakkeiden velaton hinta"
                value={calculation.calculation_variables.debt_free_price}
            />
            <BreakdownValue
                label={`- Osuus yhtiön lainoista (${formatDate(
                    calculation.calculation_variables.apartment_share_of_housing_company_loans_date
                )})`}
                value={calculation.calculation_variables.apartment_share_of_housing_company_loans}
            />
            <BreakdownValue
                label="= Enimmäismyyntihinta"
                value={calculation.maximum_price}
            />
            <BreakdownValue
                label="Velaton hinta euroa/m²"
                value={calculation.calculation_variables.debt_free_price_m2}
            />
        </>
    );
};

const SurfaceAreaPriceCeilingBreakdown = ({calculation}: {calculation: SurfaceAreaPriceCeilingCalculation}) => {
    return (
        <>
            <BreakdownValue
                label="Asunnon pinta-ala"
                value={calculation.calculation_variables.surface_area}
                unit="m²"
            />
            <BreakdownValue
                label={`* Rajaneliöhinta (${formatDate(calculation.calculation_variables.calculation_date)})`}
                value={calculation.calculation_variables.calculation_date_value}
            />
            <BreakdownValue
                label="= Velaton enimmäishinta"
                value={calculation.calculation_variables.debt_free_price}
            />
            <BreakdownValue
                label={`- Osuus yhtiön lainoista (${formatDate(
                    calculation.calculation_variables.apartment_share_of_housing_company_loans_date
                )})`}
                value={calculation.calculation_variables.apartment_share_of_housing_company_loans}
            />
            <BreakdownValue
                label="= Enimmäishinta"
                value={calculation.maximum_price}
            />
        </>
    );
};

const MaximumPriceBreakdownTabs = ({calculation}) => {
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

    return (
        <Tabs initiallyActiveTab={initiallyActiveTab()}>
            <Tabs.TabList>
                <Tabs.Tab>
                    <BreakdownTabButton
                        label="Markkinahintaindeksi"
                        calculation={calculation.calculations.market_price_index}
                    />
                </Tabs.Tab>
                <Tabs.Tab>
                    <BreakdownTabButton
                        label="Rakennuskustannusindeksi"
                        calculation={calculation.calculations.construction_price_index}
                    />
                </Tabs.Tab>
                <Tabs.Tab>
                    <BreakdownTabButton
                        label="Rajaneliöhinta"
                        calculation={calculation.calculations.surface_area_price_ceiling}
                    />
                </Tabs.Tab>
            </Tabs.TabList>
            <Tabs.TabPanel className="confirmation-modal__breakdown">
                {calculation.new_hitas ? (
                    <Breakdown2011Onwards calculation={calculation.calculations.market_price_index} />
                ) : (
                    <MarketPricePre2011Breakdown calculation={calculation.calculations.market_price_index} />
                )}
            </Tabs.TabPanel>
            <Tabs.TabPanel className="confirmation-modal__breakdown">
                {calculation.new_hitas ? (
                    <Breakdown2011Onwards calculation={calculation.calculations.construction_price_index} />
                ) : (
                    <ConstructionPricePre2011Breakdown
                        calculation={calculation.calculations.construction_price_index}
                    />
                )}
            </Tabs.TabPanel>
            <Tabs.TabPanel className="confirmation-modal__breakdown">
                <SurfaceAreaPriceCeilingBreakdown calculation={calculation.calculations.surface_area_price_ceiling} />
            </Tabs.TabPanel>
        </Tabs>
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

    return (
        <>
            <Dialog.Content>
                <MaximumPriceBreakdownTabs calculation={calculation} />
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

export default MaximumPriceModalContent;
