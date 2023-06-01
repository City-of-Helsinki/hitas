import {Fieldset, IconAlertCircleFill} from "hds-react";
import {IApartmentDetails} from "../../../common/schemas";
import {formatMoney} from "../../../common/utils";

const ApartmentCatalogPrices = ({
    apartment,
    formExtraFieldErrorMessages,
}: {
    apartment: IApartmentDetails;
    formExtraFieldErrorMessages: undefined | {catalog_acquisition_price?: string[]};
}) => {
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

export default ApartmentCatalogPrices;
