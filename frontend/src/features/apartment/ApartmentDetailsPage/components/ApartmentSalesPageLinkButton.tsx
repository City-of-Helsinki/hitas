import {Button, IconGlyphEuro} from "hds-react";
import {Link} from "react-router-dom";
import {IApartmentDetails, IHousingCompanyDetails} from "../../../../common/schemas";
import {hdsToast} from "../../../../common/utils";

const ApartmentSalesPageLinkButton = ({
    housingCompany,
    apartment,
}: {
    housingCompany: IHousingCompanyDetails;
    apartment: IApartmentDetails;
}) => {
    // If apartment has been sold for the first time, and it's company not fully completed, it can not be re-sold
    if (!housingCompany.completion_date && apartment.prices.first_purchase_date) {
        return (
            <Button
                theme="black"
                iconLeft={<IconGlyphEuro />}
                onClick={() => hdsToast.error("Valmistumattoman taloyhtiön asuntoa ei voida jälleenmyydä.")}
                disabled={housingCompany.regulation_status !== "regulated"}
            >
                Kauppatapahtuma
            </Button>
        );
    } else {
        return (
            <Link to="sales">
                <Button
                    theme="black"
                    iconLeft={<IconGlyphEuro />}
                    disabled={housingCompany.regulation_status !== "regulated" || !apartment.surface_area}
                >
                    Kauppatapahtuma
                </Button>
            </Link>
        );
    }
};

export default ApartmentSalesPageLinkButton;
