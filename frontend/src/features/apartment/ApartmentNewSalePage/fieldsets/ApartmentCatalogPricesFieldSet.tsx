import {Fieldset} from "hds-react";
import {useContext, useEffect} from "react";
import SimpleErrorMessage from "../../../../common/components/SimpleErrorMessage";
import {formatMoney} from "../../../../common/utils";
import {ApartmentSaleContext} from "../utils";

const ApartmentCatalogPricesFieldSet = () => {
    const {apartment, formExtraFieldErrorMessages, setMaximumPrices} = useContext(ApartmentSaleContext);

    // Set maximum prices to state when component is loaded
    useEffect(() => {
        setMaximumPrices({
            maximumPrice: apartment.prices.catalog_purchase_price ?? 0,
            debtFreePurchasePrice: apartment.prices.catalog_acquisition_price ?? 0,
            apartmentShareOfHousingCompanyLoans: apartment.prices.catalog_share_of_housing_company_loans ?? 0,
            index: "",
        });
    }, []);

    const maximumPrices = {
        maximumPrice: apartment.prices.catalog_purchase_price ?? 0,
        debtFreePurchasePrice: apartment.prices.catalog_acquisition_price ?? 0,
        apartmentShareOfHousingCompanyLoans: apartment.prices.catalog_share_of_housing_company_loans ?? 0,
        index: "",
    };

    const errorMessage =
        formExtraFieldErrorMessages?.catalog_acquisition_price &&
        formExtraFieldErrorMessages.catalog_acquisition_price[0];

    return (
        <Fieldset heading="Myyntihintaluettelon hinnat">
            <div className="max-prices">
                <div className="row row--max-prices">
                    <div className="fieldset--max-prices__value">
                        <legend>Myyntihinta (€)</legend>
                        <span className="">{formatMoney(maximumPrices.maximumPrice)}</span>
                    </div>
                    <div className="fieldset--max-prices__value">
                        <legend>Osuus yhtiön lainoista (€)</legend>
                        <span>{formatMoney(maximumPrices.apartmentShareOfHousingCompanyLoans)}</span>
                    </div>
                    <div className="fieldset--max-prices__value">
                        <legend>Velaton enimmäishinta (€)</legend>
                        <span>{formatMoney(maximumPrices.debtFreePurchasePrice)}</span>
                    </div>
                </div>

                <SimpleErrorMessage errorMessage={errorMessage} />
            </div>
        </Fieldset>
    );
};

export default ApartmentCatalogPricesFieldSet;
