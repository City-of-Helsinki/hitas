import {Fieldset} from "hds-react";
import {useContext} from "react";
import {CheckboxInput, DateInput, NumberInput} from "../../../../common/components/forms";
import {ApartmentSaleContext} from "../utils";

const ApartmentSaleFormFieldSet = () => {
    const {apartment, formExtraFieldErrorMessages} = useContext(ApartmentSaleContext);

    const isApartmentFirstSale = !apartment?.prices.first_purchase_date;
    const isFormDateFieldsInvalid =
        formExtraFieldErrorMessages &&
        !!(formExtraFieldErrorMessages.purchase_date || formExtraFieldErrorMessages.notification_date);

    return (
        <Fieldset heading="Kaupan tiedot">
            <div className="row">
                <DateInput
                    name="notification_date"
                    label="Ilmoituspäivämäärä"
                    maxDate={new Date()}
                    required
                />
                <DateInput
                    name="purchase_date"
                    label="Kauppakirjan päivämäärä"
                    maxDate={new Date()}
                    required
                />
            </div>
            <div className="row">
                <NumberInput
                    name="purchase_price"
                    label="Kauppahinta"
                    unit="€"
                    required
                    disabled={isFormDateFieldsInvalid}
                />
                <NumberInput
                    name="apartment_share_of_housing_company_loans"
                    label="Osuus yhtiön lainoista"
                    unit="€"
                    required
                    disabled={isFormDateFieldsInvalid}
                />
            </div>
            {!isApartmentFirstSale ? (
                <CheckboxInput
                    name="exclude_from_statistics"
                    label="Ei tilastoihin (esim. sukulaiskauppa)"
                    triggerField="purchase_price"
                    disabled={isFormDateFieldsInvalid}
                />
            ) : null}
        </Fieldset>
    );
};

export default ApartmentSaleFormFieldSet;
