import {Fieldset} from "hds-react";
import {useContext} from "react";
import {useFormContext} from "react-hook-form";
import {CheckboxInput, DateInput, NumberInput} from "../../../../common/components/form";
import {ApartmentSaleContext} from "../utils";

const ApartmentSaleFormFieldSet = ({formRef, onSubmit}) => {
    const saleForm = useFormContext();

    const {apartment, formExtraFieldErrorMessages} = useContext(ApartmentSaleContext);

    const isApartmentFirstSale = !apartment?.prices.first_purchase_date;
    const isFormDateFieldsInvalid =
        formExtraFieldErrorMessages &&
        !!(formExtraFieldErrorMessages.purchase_date || formExtraFieldErrorMessages.notification_date);

    return (
        <Fieldset heading="Kaupan tiedot">
            <form
                ref={formRef}
                onSubmit={onSubmit}
            >
                <div className="row">
                    <DateInput
                        name="notification_date"
                        label="Ilmoituspäivämäärä"
                        formObject={saleForm}
                        maxDate={new Date()}
                        required
                    />
                    <DateInput
                        name="purchase_date"
                        label="Kauppakirjan päivämäärä"
                        formObject={saleForm}
                        maxDate={new Date()}
                        required
                    />
                </div>
                <div className="row">
                    <NumberInput
                        name="purchase_price"
                        label="Kauppahinta"
                        formObject={saleForm}
                        unit="€"
                        required
                        disabled={isFormDateFieldsInvalid}
                    />
                    <NumberInput
                        name="apartment_share_of_housing_company_loans"
                        label="Osuus yhtiön lainoista"
                        formObject={saleForm}
                        unit="€"
                        required
                        disabled={isFormDateFieldsInvalid}
                    />
                </div>
                {!isApartmentFirstSale ? (
                    <CheckboxInput
                        name="exclude_from_statistics"
                        label="Ei tilastoihin (esim. sukulaiskauppa)"
                        formObject={saleForm}
                        triggerField="purchase_price"
                        disabled={isFormDateFieldsInvalid}
                    />
                ) : null}
            </form>
        </Fieldset>
    );
};

export default ApartmentSaleFormFieldSet;
