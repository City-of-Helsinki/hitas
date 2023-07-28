import {Button, Card, IconGlyphEuro, IconLock} from "hds-react";
import {Link} from "react-router-dom";
import {IApartmentConditionOfSale, IApartmentDetails, IHousingCompanyDetails} from "../../../../common/schemas";
import {formatAddress, formatOwner, hdsToast} from "../../../../common/utils";
import ConditionsOfSaleStatus from "../../components/ConditionsOfSaleStatus";

const ApartmentSaleButton = ({onClick, disabled}) => {
    return (
        <Button
            theme="black"
            iconLeft={<IconGlyphEuro />}
            onClick={onClick}
            disabled={disabled}
        >
            Kauppatapahtuma
        </Button>
    );
};

const ApartmentSalesPageLinkButton = ({
    housingCompany,
    apartment,
}: {
    housingCompany: IHousingCompanyDetails;
    apartment: IApartmentDetails;
}) => {
    let apartmentCantBeSoldErrorMessage;

    if (!apartment.surface_area) {
        apartmentCantBeSoldErrorMessage = "Asunnolta puuttuu pinta-ala";
    } else if (apartment.prices.first_purchase_date && !housingCompany.completion_date) {
        // If apartment has been sold for the first time, and it's company not fully completed, it can not be re-sold
        apartmentCantBeSoldErrorMessage = "Valmistumattoman taloyhtiön asuntoa ei voida jälleenmyydä";
    } else if (apartment.prices.first_purchase_date && housingCompany.hitas_type === "half_hitas") {
        apartmentCantBeSoldErrorMessage = "Puolihitas-taloyhtiön asuntoa ei voida jälleenmyydä";
    } else if (housingCompany.regulation_status !== "regulated") {
        apartmentCantBeSoldErrorMessage = "Vapautetun taloyhtiön asuntoa ei voida jälleenmyydä";
    }

    if (apartmentCantBeSoldErrorMessage) {
        return (
            <ApartmentSaleButton
                onClick={() => hdsToast.error(apartmentCantBeSoldErrorMessage)}
                disabled={housingCompany.regulation_status !== "regulated"}
            />
        );
    } else {
        return (
            <Link to="sales">
                <ApartmentSaleButton
                    onClick={undefined}
                    disabled={housingCompany.regulation_status !== "regulated"}
                />
            </Link>
        );
    }
};

const SingleApartmentConditionOfSale = ({conditionsOfSale}: {conditionsOfSale: IApartmentConditionOfSale[]}) => {
    return (
        <li>
            <h3>{formatOwner(conditionsOfSale[0].owner)}</h3>
            <ul>
                {conditionsOfSale.map((cos) => (
                    <li
                        key={cos.id}
                        className={cos.fulfilled ? "resolved" : "unresolved"}
                    >
                        <Link
                            to={`/housing-companies/${cos.apartment.housing_company.id}/apartments/${cos.apartment.id}`}
                        >
                            <ConditionsOfSaleStatus conditionOfSale={cos} />
                            <span className="address">{formatAddress(cos.apartment.address)}</span>
                        </Link>
                    </li>
                ))}
            </ul>
        </li>
    );
};

const ApartmentConditionsOfSaleCard = ({
    apartment,
    housingCompany,
}: {
    apartment: IApartmentDetails;
    housingCompany: IHousingCompanyDetails;
}) => {
    const conditionsOfSale = apartment.conditions_of_sale;

    // Create a dict with owner id as key, and all of their conditions of sale in a list as value
    interface IGroupedConditionsOfSale {
        [ownerId: string]: IApartmentConditionOfSale[];
    }

    const groupedConditionsOfSale: IGroupedConditionsOfSale = conditionsOfSale.reduce((acc, obj) => {
        if (obj.owner.id in acc) {
            acc[obj.owner.id].push(obj);
        } else {
            acc[obj.owner.id] = [obj];
        }
        return acc;
    }, {});
    // Order owners with unfulfilled conditions of sale first.
    // When owners have the same amount of unfulfilled conditions of sale, owners with more total COS are last.
    const sortedKeys = Object.keys(groupedConditionsOfSale).sort((a, b) => {
        const diff =
            groupedConditionsOfSale[b].filter((cos) => !cos.fulfilled).length -
            groupedConditionsOfSale[a].filter((cos) => !cos.fulfilled).length;
        if (diff !== 0) return diff;
        return groupedConditionsOfSale[a].length - groupedConditionsOfSale[b].length;
    });

    return (
        <Card>
            <div className="row row--buttons">
                <ApartmentSalesPageLinkButton
                    housingCompany={housingCompany}
                    apartment={apartment}
                />
                <Link to="conditions-of-sale">
                    <Button
                        theme="black"
                        iconLeft={<IconLock />}
                        disabled={!apartment.ownerships.length || housingCompany.regulation_status !== "regulated"}
                    >
                        Muokkaa myyntiehtoja
                    </Button>
                </Link>
            </div>
            <label className="card-heading card-heading--conditions-of-sale">Myyntiehdot</label>
            {Object.keys(groupedConditionsOfSale).length ? (
                <ul>
                    {sortedKeys.map((ownerId) => (
                        <SingleApartmentConditionOfSale
                            key={ownerId}
                            conditionsOfSale={
                                // Sort owners conditions of sale by unfulfilled first
                                groupedConditionsOfSale[ownerId].sort((a, b) =>
                                    !!a.fulfilled === !!b.fulfilled ? 0 : a.fulfilled ? 1 : -1
                                )
                            }
                        />
                    ))}
                </ul>
            ) : (
                <span className="no-conditions">Ei myyntiehtoja.</span>
            )}
        </Card>
    );
};

export default ApartmentConditionsOfSaleCard;
