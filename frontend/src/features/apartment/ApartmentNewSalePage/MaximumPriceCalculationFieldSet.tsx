import {Fieldset} from "hds-react";
import {formatDate} from "../../../common/utils";
import MaximumPriceCalculationExists from "./MaximumPriceCalculationExists";
import MaximumPriceCalculationMissing from "./MaximumPriceCalculationMissing";

const MaximumPriceCalculationFieldSet = ({
    apartment,
    maxPriceCalculation,
    hasLoanValueChanged,
    purchasePrice,
    maxPrices,
    warningsGiven,
    maxPriceData,
    handleCalculateButton,
    isCalculationFormValid,
    saleForm,
}) => {
    return (
        <Fieldset
            heading={`Enimmäishintalaskelma ${
                maxPriceCalculation
                    ? `(vahvistettu ${formatDate(apartment.prices.maximum_prices.confirmed?.confirmed_at as string)})`
                    : ""
            } *`}
        >
            {maxPriceCalculation ? (
                <MaximumPriceCalculationExists
                    maxPriceCalculation={maxPriceCalculation}
                    hasLoanValueChanged={hasLoanValueChanged}
                    purchasePrice={purchasePrice}
                    maxPrices={maxPrices}
                    warningsGiven={warningsGiven}
                    maxPriceData={maxPriceData}
                    handleCalculateButton={handleCalculateButton}
                    isCalculationFormValid={isCalculationFormValid}
                />
            ) : (
                <MaximumPriceCalculationMissing
                    handleCalculateButton={handleCalculateButton}
                    saleForm={saleForm}
                />
            )}
        </Fieldset>
    );
};

export default MaximumPriceCalculationFieldSet;
