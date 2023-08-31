import {useContext, useEffect} from "react";
import {useFormContext} from "react-hook-form";
import {QueryStateHandler} from "../../../../../common/components";
import {getIndexType} from "../../../../../common/localisation";
import {IApartmentMaximumPriceCalculationDetails} from "../../../../../common/schemas";
import {useGetApartmentMaximumPriceQuery} from "../../../../../common/services";
import {formatDate, formatMoney, hdsToast} from "../../../../../common/utils";
import {ApartmentSaleContext} from "../../utils";

// Element to display when there is a valid maximum price calculation for the apartment
const LoadedMaximumPriceCalculationExists = ({
    maximumPriceCalculation,
}: {
    maximumPriceCalculation: IApartmentMaximumPriceCalculationDetails;
}) => {
    const {formExtraFieldErrorMessages} = useContext(ApartmentSaleContext);
    const {getValues} = useFormContext();

    const indexVariables = maximumPriceCalculation.calculations[maximumPriceCalculation.index].calculation_variables;
    const maximumPrices = {
        maximumPrice: maximumPriceCalculation.maximum_price,
        maxPricePerSquare: maximumPriceCalculation.maximum_price_per_square,
        debtFreePurchasePrice: indexVariables.debt_free_price,
        apartmentShareOfHousingCompanyLoans: indexVariables.apartment_share_of_housing_company_loans,
        index: maximumPriceCalculation.index,
    };

    const hasLoanValueChanged = formExtraFieldErrorMessages?.apartment_share_of_housing_company_loans;

    return (
        <div className={`max-prices${hasLoanValueChanged ? " expired" : ""}`}>
            <div className="row row--max-prices">
                <div className="fieldset--max-prices__value">
                    <legend>Enimmäishinta (€)</legend>
                    <span className={getValues("purchase_price") > maximumPrices.maximumPrice ? "error-text" : ""}>
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

            <p>
                Enimmäishinnat on laskettu
                <span>{` ${getIndexType(maximumPrices.index)}llä`}</span> sekä{" "}
                <span>
                    {maximumPrices.apartmentShareOfHousingCompanyLoans === 0
                        ? "0 €"
                        : formatMoney(maximumPrices.apartmentShareOfHousingCompanyLoans)}
                </span>{" "}
                lainaosuudella.
                <br />
                Laskelma on voimassa <span>{formatDate(maximumPriceCalculation.calculation_date)}</span> ─{" "}
                <span>{formatDate(maximumPriceCalculation.valid_until)}</span>.
                <br />
                Vahvistettu <span>{formatDate(maximumPriceCalculation.confirmed_at)}</span>.
            </p>
        </div>
    );
};

const MaximumPriceCalculationExists = () => {
    const {apartment, setMaximumPrices} = useContext(ApartmentSaleContext);
    const {setValue} = useFormContext();

    const {
        data: maximumPriceCalculationData,
        error: maximumPriceError,
        isLoading: isMaximumPriceLoading,
    } = useGetApartmentMaximumPriceQuery(
        {
            housingCompanyId: apartment?.links.housing_company.id,
            apartmentId: apartment?.id,
            priceId: apartment?.prices.maximum_prices.confirmed?.id as string,
        },
        {skip: !apartment?.prices.maximum_prices.confirmed?.id}
    );

    const handleSetMaxPrices = (calculation: IApartmentMaximumPriceCalculationDetails) => {
        const indexVariables = calculation.calculations[calculation.index].calculation_variables;
        setMaximumPrices({
            maximumPrice: calculation.maximum_price,
            debtFreePurchasePrice: indexVariables.debt_free_price,
            apartmentShareOfHousingCompanyLoans: indexVariables.apartment_share_of_housing_company_loans,
            index: calculation.index,
        });

        setValue("purchase_date", calculation.calculation_date);
        setValue("apartment_share_of_housing_company_loans", indexVariables.apartment_share_of_housing_company_loans);
    };

    useEffect(() => {
        if (isMaximumPriceLoading || !maximumPriceCalculationData) return;
        if (maximumPriceCalculationData && !maximumPriceError) {
            handleSetMaxPrices(maximumPriceCalculationData);
        } else {
            hdsToast.error("Enimmäishintalaskelman hakeminen epäonnistui.");
        }
        // eslint-disable-next-line
    }, [maximumPriceCalculationData, maximumPriceError, isMaximumPriceLoading]);

    return (
        <QueryStateHandler
            data={maximumPriceCalculationData}
            error={maximumPriceError}
            isLoading={isMaximumPriceLoading}
        >
            <LoadedMaximumPriceCalculationExists
                maximumPriceCalculation={maximumPriceCalculationData as IApartmentMaximumPriceCalculationDetails}
            />
        </QueryStateHandler>
    );
};

export default MaximumPriceCalculationExists;
