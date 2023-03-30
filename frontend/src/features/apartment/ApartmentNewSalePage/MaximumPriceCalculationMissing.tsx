import {Button} from "hds-react";

// Element to display when there is no valid maximum price calculation for the apartment
const MaximumPriceCalculationMissing = ({handleCalculateButton, isCalculationFormValid}) => {
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
                disabled={!isCalculationFormValid}
            >
                Luo enimmäishintalaskelma
            </Button>
        </div>
    );
};

export default MaximumPriceCalculationMissing;
