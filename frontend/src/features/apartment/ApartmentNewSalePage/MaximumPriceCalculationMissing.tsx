import {useContext} from "react";
import {formatMoney, getApartmentUnconfirmedPrices} from "../../../common/utils";
import {ApartmentSaleContext} from "./index";

// Element to display when there is no valid maximum price calculation for the apartment
const MaximumPriceCalculationMissing = () => {
    const {apartment} = useContext(ApartmentSaleContext);
    if (!apartment) return null;

    const unconfirmedPrices = getApartmentUnconfirmedPrices(apartment);

    return (
        <div className="row row--prompt">
            <p>
                Asunnosta ei ole vahvistettua enimmäishintalaskelmaa.
                {unconfirmedPrices.surface_area_price_ceiling.value ? (
                    <>
                        Enimmäishintana käytetään asunnon rajaneliöhinta-arviota
                        <b> {formatMoney(unconfirmedPrices.surface_area_price_ceiling.value)}.</b>
                        <br />
                        Mikäli asunnon velaton kauppahinta ylittää rajaneliöhinta-arvion, tulee asunnolle luoda
                        vahvistettu enimmäishintalaskelma.
                    </>
                ) : (
                    <b> Asunnon rajaneliöhinta-arviota ei voitu laskea.</b>
                )}
            </p>
        </div>
    );
};

export default MaximumPriceCalculationMissing;
