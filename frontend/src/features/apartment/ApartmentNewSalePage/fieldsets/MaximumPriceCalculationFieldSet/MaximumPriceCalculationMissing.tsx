import {useContext} from "react";
import {formatMoney, getApartmentUnconfirmedPrices} from "../../../../../common/utils";
import {ApartmentSaleContext} from "../../utils";

// Element to display when there is no valid maximum price calculation for the apartment
const MaximumPriceCalculationMissing = () => {
    const {apartment} = useContext(ApartmentSaleContext);

    const unconfirmedPrices = getApartmentUnconfirmedPrices(apartment);

    return (
        <div className="row row--max-prices--unconfirmed">
            <>
                <p>Asunnosta ei ole vahvistettua enimmäishintalaskelmaa valitulle kauppakirjan päivämäärälle.</p>
                {unconfirmedPrices.surface_area_price_ceiling.value ? (
                    <>
                        <p>
                            Enimmäishintana käytetään asunnon rajaneliöhinta-arviota
                            <span> {formatMoney(unconfirmedPrices.surface_area_price_ceiling.value)}.</span>
                        </p>
                        <p>
                            Mikäli asunnon velaton kauppahinta ylittää rajaneliöhinta-arvion, tulee asunnolle luoda
                            vahvistettu enimmäishintalaskelma.
                        </p>
                    </>
                ) : (
                    <b> Asunnon rajaneliöhinta-arviota ei voitu laskea.</b>
                )}
            </>
        </div>
    );
};

export default MaximumPriceCalculationMissing;
