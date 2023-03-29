import {Button} from "hds-react";

// Element to display when there is no valid maximum price calculation for the apartment
// TODO: Will this ever be shown? If some sort of calculation will be generated if there is none, we should never end up showing this element.
const MaximumPriceCalculationMissing = ({handleCalculateButton, saleForm}) => {
    return (
        <div className="row row--prompt">
            <p>
                Asunnosta ei ole vahvistettua enimmäishintalaskelmaa, tai se ei ole enää voimassa. Syötä{" "}
                <span>kauppakirjan päivämäärä</span> sekä <span>yhtiön lainaosuus</span>, ja tee sitten uusi
                enimmäishintalaskelma saadaksesi asunnon enimmäishinnat kauppaa varten.
            </p>
            <Button
                theme="black"
                onClick={handleCalculateButton}
                disabled={
                    !saleForm.getValues("purchase_date") ||
                    isNaN(Number(saleForm.getValues("apartment_share_of_housing_company_loans")))
                }
            >
                Tee enimmäishintalaskelma
            </Button>
        </div>
    );
};

export default MaximumPriceCalculationMissing;
