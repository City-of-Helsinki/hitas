import {Button} from "hds-react";
import {IApartmentDetails} from "../../../common/schemas";
import {formatMoney, getApartmentUnconfirmedPrices} from "../../../common/utils";

// Element to display when there is no valid maximum price calculation for the apartment
const MaximumPriceCalculationMissing = ({
    apartment,
    handleCalculateButton,
    isCalculationFormValid,
}: {
    apartment: IApartmentDetails;
    handleCalculateButton: () => void;
    isCalculationFormValid: boolean;
}) => {
    const unconfirmedPrices = getApartmentUnconfirmedPrices(apartment);

    return (
        <div className="row row--prompt">
            <p>
                Asunnosta ei ole vahvistettua enimmäishintalaskelmaa. Enimmäishintana käytetään asunnon
                rajaneliöhinta-arviota <b>{formatMoney(unconfirmedPrices.surface_area_price_ceiling.value)}.</b>
                <br />
                Mikäli asunnon velaton kauppahinta ylittää rajaneliöhinta-arvion, tulee asunnolle luoda vahvistettu
                enimmäishintalaskelma.
            </p>

            <Button
                theme="black"
                onClick={handleCalculateButton}
                disabled={!isCalculationFormValid}
            >
                Luo enimmäishintalaskelma
            </Button>
        </div>
    );
};

export default MaximumPriceCalculationMissing;
