import React, {useEffect} from "react";

import {Button, Dialog, Tabs} from "hds-react";
import {useNavigate} from "react-router-dom";

import {useSaveApartmentMaximumPriceMutation} from "../../../app/services";
import {SaveButton} from "../../../common/components";
import {IApartmentDetails, IApartmentMaximumPrice} from "../../../common/models";
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

const MarketPriceBreakdown = ({calculation}) => {
    const variables = calculation.calculations.market_price_index.calculation_variables;
    return (
        <>
            <BreakdownValue
                label="Hankinta-arvo"
                value={variables.acquisition_price}
            />
            <BreakdownValue
                label="+ Rakennusaikaiset lisä- ja muutostyöt"
                value={variables.additional_work_during_construction}
            />
            <BreakdownValue
                label="= Perushinta"
                value={variables.basic_price}
            />
            <BreakdownValue
                label="+ Indeksin muutos"
                value={variables.index_adjustment}
            />
            <BreakdownValue
                label="+ Huoneistokohtaiset parannukset"
                value={variables.apartment_improvements?.summary.value}
            />
            <BreakdownValue
                label="+ Osuus yhtiön parannuksista"
                value={variables.housing_company_improvements?.summary.value_for_apartment}
            />
            <BreakdownValue
                label="= Osakkeiden velaton hinta"
                value={variables.debt_free_price}
            />
            <BreakdownValue
                label={`- Osuus yhtiön lainoista (${formatDate(
                    variables.apartment_share_of_housing_company_loans_date
                )})`}
                value={variables.apartment_share_of_housing_company_loans}
            />
            <BreakdownValue
                label="= Enimmäismyyntihinta"
                value={calculation.calculations.market_price_index.maximum_price}
            />
            <BreakdownValue
                label="Velaton hinta euroa/m²"
                value={variables.debt_free_price_m2}
            />
        </>
    );
};

const ConstructionPriceBreakdown = ({calculation}) => {
    const variables = calculation.calculations.construction_price_index.calculation_variables;
    return (
        <>
            <BreakdownValue
                label="Hankinta-arvo"
                value={variables.acquisition_price}
            />
            <BreakdownValue
                label="+ Rakennusaikaiset lisä- ja muutostyöt"
                value={variables.additional_work_during_construction}
            />
            <BreakdownValue
                label="= Perushinta"
                value={variables.basic_price}
            />
            <BreakdownValue
                label="+ Indeksin muutos"
                value={variables.index_adjustment}
            />
            <BreakdownValue
                label="+ Huoneistokohtaiset parannukset"
                value={variables.apartment_improvements?.summary.value}
            />
            <BreakdownValue
                label="+ Osuus yhtiön parannuksista"
                value={variables.housing_company_improvements?.summary.value_for_apartment}
            />
            <BreakdownValue
                label="= Osakkeiden velaton hinta"
                value={variables.debt_free_price}
            />
            <BreakdownValue
                label={`- Osuus yhtiön lainoista (${formatDate(
                    variables.apartment_share_of_housing_company_loans_date
                )})`}
                value={variables.apartment_share_of_housing_company_loans}
            />
            <BreakdownValue
                label="= Enimmäismyyntihinta"
                value={calculation.calculations.construction_price_index.maximum_price}
            />
            <BreakdownValue
                label="Velaton hinta euroa/m²"
                value={variables.debt_free_price_m2}
            />
        </>
    );
};

const SurfaceAreaPriceCeilingBreakdown = ({calculation}) => {
    const variables = calculation.calculations.surface_area_price_ceiling.calculation_variables;
    return (
        <>
            <BreakdownValue
                label="Asunnon pinta-ala"
                value={variables.surface_area}
                unit="m²"
            />
            <BreakdownValue
                label={`* Rajaneliöhinta (${formatDate(variables.calculation_date)})`}
                value={variables.calculation_date_value}
            />
            <BreakdownValue
                label="= Velaton enimmäishinta"
                value={variables.debt_free_price}
            />
            <BreakdownValue
                label={`- Osuus yhtiön lainoista (${formatDate(
                    variables.apartment_share_of_housing_company_loans_date
                )})`}
                value={variables.apartment_share_of_housing_company_loans}
            />
            <BreakdownValue
                label="= Enimmäishinta"
                value={calculation.calculations.surface_area_price_ceiling.maximum_price}
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
                <MarketPriceBreakdown calculation={calculation} />
            </Tabs.TabPanel>
            <Tabs.TabPanel className="confirmation-modal__breakdown">
                <ConstructionPriceBreakdown calculation={calculation} />
            </Tabs.TabPanel>
            <Tabs.TabPanel className="confirmation-modal__breakdown">
                <SurfaceAreaPriceCeilingBreakdown calculation={calculation} />
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
