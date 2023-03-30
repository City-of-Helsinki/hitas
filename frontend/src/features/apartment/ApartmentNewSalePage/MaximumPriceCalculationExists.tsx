import {Button, IconAlertCircleFill} from "hds-react";
import {getIndexType} from "../../../common/localisation";
import {formatMoney} from "../../../common/utils";

// Element to display when there is a valid maximum price calculation for the apartment
const MaximumPriceCalculationExists = ({
    saleForm,
    maximumPriceCalculation,
    handleCalculateButton,
    isCalculationFormValid,
}) => {
    const indexVariables = maximumPriceCalculation.calculations[maximumPriceCalculation.index].calculation_variables;
    const maximumPrices = {
        maximumPrice: maximumPriceCalculation.maximum_price,
        maxPricePerSquare: maximumPriceCalculation.maximum_price_per_square,
        debtFreePurchasePrice: indexVariables.debt_free_price,
        apartmentShareOfHousingCompanyLoans: indexVariables.apartment_share_of_housing_company_loans,
        index: maximumPriceCalculation.index,
    };

    const hasLoanValueChanged =
        saleForm.getValues("apartment_share_of_housing_company_loans") !==
        maximumPrices.apartmentShareOfHousingCompanyLoans;

    return (
        <div className={`max-prices${hasLoanValueChanged ? " expired" : ""}`}>
            <div className="row row--max-prices">
                <div className="fieldset--max-prices__value">
                    <legend>Enimmäishinta (€)</legend>
                    <span
                        className={
                            saleForm.getValues("purchase_price") > maximumPrices.maximumPrice ? "error-text" : ""
                        }
                    >
                        {formatMoney(maximumPrices.maximumPrice)}
                    </span>
                </div>
                <div className="fieldset--max-prices__value">
                    <legend>Enimmäishinta per m² (€)</legend>
                    <span>{formatMoney(maximumPrices.maxPricePerSquare)}</span>
                </div>
                <div className="fieldset--max-prices__value">
                    <legend>Velaton enimmäishinta (€)</legend>
                    <span>{formatMoney(maximumPrices.debtFreePurchasePrice)}</span>
                </div>
            </div>

            <div className="row row--prompt">
                <p>
                    Enimmäishinnat on laskettu
                    <span>{` ${getIndexType(maximumPrices.index)}llä`}</span> sekä{" "}
                    <span>
                        {maximumPrices.apartmentShareOfHousingCompanyLoans === 0
                            ? "0 €"
                            : formatMoney(maximumPrices.apartmentShareOfHousingCompanyLoans)}
                    </span>{" "}
                    lainaosuudella.
                </p>
                {hasLoanValueChanged && (
                    <p className="error-text">
                        <IconAlertCircleFill />
                        <span>Yhtiön lainaosuus</span> on muuttunut, ole hyvä ja
                        <span> tee uusi enimmäishintalaskelma</span>.
                    </p>
                )}
                <Button
                    theme="black"
                    variant={hasLoanValueChanged ? "primary" : "secondary"}
                    onClick={handleCalculateButton}
                    disabled={!isCalculationFormValid}
                >
                    Luo uusi enimmäishintalaskelma
                </Button>
            </div>
        </div>
    );
};

export default MaximumPriceCalculationExists;
