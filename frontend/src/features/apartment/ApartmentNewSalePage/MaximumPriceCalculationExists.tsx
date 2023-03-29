// Element to display when there is a valid maximum price calculation for the apartment
import {Button, IconAlertCircleFill} from "hds-react";
import {getIndexType} from "../../../common/localisation";
import {formatMoney} from "../../../common/utils";

const MaximumPriceCalculationExists = ({
    maxPriceCalculation,
    hasLoanValueChanged,
    purchasePrice,
    maxPrices,
    warningsGiven,
    maxPriceData,
    handleCalculateButton,
    isCalculationFormValid,
}) => {
    return (
        <div className={`max-prices${hasLoanValueChanged ? " expired" : ""}`}>
            <div className="row row--max-prices">
                <div className="fieldset--max-prices__value">
                    <legend>Enimmäishinta (€)</legend>
                    <span
                        className={
                            purchasePrice > (maxPrices.maximumPrice as number) && !warningsGiven.purchase_price
                                ? "error-text"
                                : ""
                        }
                    >
                        {formatMoney(maxPrices.maximumPrice as number)}
                    </span>
                </div>
                <div className="fieldset--max-prices__value">
                    <legend>Enimmäishinta per m² (€)</legend>
                    <span>{formatMoney(maxPrices.maxPricePerSquare)}</span>
                </div>
                <div className="fieldset--max-prices__value">
                    <legend>Velaton enimmäishinta (€)</legend>
                    <span>{formatMoney(maxPrices.debtFreePurchasePrice)}</span>
                </div>
            </div>

            <div className="row row--prompt">
                <p>
                    Enimmäishinnat on laskettu{" "}
                    <span>{` ${getIndexType(maxPriceData ? maxPriceData.index : maxPriceCalculation.index)}llä`}</span>{" "}
                    sekä{" "}
                    <span>
                        {maxPriceCalculation?.calculations[maxPriceCalculation.index].calculation_variables
                            .apartment_share_of_housing_company_loans === 0
                            ? "0 €"
                            : formatMoney(
                                  maxPriceCalculation?.calculations[maxPriceCalculation.index].calculation_variables
                                      .apartment_share_of_housing_company_loans
                              )}
                    </span>{" "}
                    lainaosuudella.{" "}
                </p>
                {!!hasLoanValueChanged && (
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
                    disabled={!isCalculationFormValid().success}
                >
                    Tee uusi enimmäishintalaskelma
                </Button>
            </div>
        </div>
    );
};

export default MaximumPriceCalculationExists;
