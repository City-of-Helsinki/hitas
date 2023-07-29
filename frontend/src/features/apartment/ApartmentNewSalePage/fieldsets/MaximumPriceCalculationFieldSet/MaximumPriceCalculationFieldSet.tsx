import {Fieldset} from "hds-react";
import {useContext} from "react";
import {useFormContext} from "react-hook-form";
import {SimpleErrorMessage} from "../../../../../common/components";
import CreateMaximumPriceCalculationButton from "../../../components/MaximumPriceCalculationCreateButton";
import {ApartmentSaleContext, isApartmentMaxPriceCalculationValid} from "../../utils";
import MaximumPriceCalculationExists from "./MaximumPriceCalculationExists";
import MaximumPriceCalculationMissing from "./MaximumPriceCalculationMissing";

const MaximumPriceCalculationFieldSet = () => {
    const {apartment, formExtraFieldErrorMessages} = useContext(ApartmentSaleContext);
    const formObject = useFormContext();

    const isCalculationValid = isApartmentMaxPriceCalculationValid(apartment, formObject.watch("purchase_date"));

    const hasLoanValueChanged =
        formExtraFieldErrorMessages?.apartment_share_of_housing_company_loans &&
        formObject.watch("apartment_share_of_housing_company_loans") !== null;

    const maximumPriceCalculationErrorMessage =
        formExtraFieldErrorMessages?.maximum_price_calculation &&
        formExtraFieldErrorMessages.maximum_price_calculation[0];

    const getParsedFormData = () => {
        const date = formObject.getValues("purchase_date") ?? null;
        return {
            calculation_date: date,
            apartment_share_of_housing_company_loans_date: date,
            apartment_share_of_housing_company_loans:
                formObject.getValues("apartment_share_of_housing_company_loans") ?? 0,
            additional_info: "",
        };
    };

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

            <CreateMaximumPriceCalculationButton
                buttonVariant={hasLoanValueChanged ? "primary" : "secondary"}
                getParsedFormData={getParsedFormData}
            />
        </Fieldset>
    );
};

export default MaximumPriceCalculationFieldSet;
