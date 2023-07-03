import {Fieldset} from "hds-react";
import {useContext} from "react";
import {useFormContext} from "react-hook-form";
import {SimpleErrorMessage} from "../../../../../common/components";
import {ApartmentSaleContext, isApartmentMaxPriceCalculationValid} from "../../utils";
import MaximumPriceCalculationCreateButton from "./MaximumPriceCalculationCreateButton";
import MaximumPriceCalculationExists from "./MaximumPriceCalculationExists";
import MaximumPriceCalculationMissing from "./MaximumPriceCalculationMissing";

const MaximumPriceCalculationFieldSet = () => {
    const {apartment, formExtraFieldErrorMessages} = useContext(ApartmentSaleContext);
    const saleForm = useFormContext();

    const isCalculationValid = isApartmentMaxPriceCalculationValid(apartment, saleForm.watch("purchase_date"));

    const hasLoanValueChanged =
        formExtraFieldErrorMessages?.apartment_share_of_housing_company_loans &&
        saleForm.watch("apartment_share_of_housing_company_loans") !== null;

    const maximumPriceCalculationErrorMessage =
        formExtraFieldErrorMessages?.maximum_price_calculation &&
        formExtraFieldErrorMessages.maximum_price_calculation[0];

    return (
        <Fieldset
            heading="Enimmäishintalaskelma"
            tooltipText="Tässä näytetään uusin vahvistettu enimmäishintalaskelma. Mikäli vahvistettua enimmäishintalaskelmaa ei ole tai se ei ole kauppakirjan päivämääränä voimassa, näytetään asunnon rajaneliöhinta-arvio."
        >
            {isCalculationValid ? <MaximumPriceCalculationExists /> : <MaximumPriceCalculationMissing />}

            <SimpleErrorMessage errorMessage={maximumPriceCalculationErrorMessage} />
            <SimpleErrorMessage
                errorMessage={
                    hasLoanValueChanged && (
                        <>
                            <span>Yhtiön lainaosuus</span> on muuttunut, ole hyvä ja
                            <span> tee uusi enimmäishintalaskelma</span>.
                        </>
                    )
                }
            />

            <MaximumPriceCalculationCreateButton hasLoanValueChanged={hasLoanValueChanged} />
        </Fieldset>
    );
};

export default MaximumPriceCalculationFieldSet;
