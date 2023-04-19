import {IconLock, StatusLabel} from "hds-react";
import {Link, useLocation} from "react-router-dom";

import {EditButton, Heading} from "../../../common/components";
import {getApartmentStateLabel} from "../../../common/localisation";
import {IApartmentDetails} from "../../../common/schemas";
import {formatAddress} from "../../../common/utils";

const ApartmentHeader = ({
    apartment,
    showEditButton = false,
}: {
    apartment: IApartmentDetails;
    showEditButton?: boolean;
}) => {
    const {pathname} = useLocation();
    const isApartmentSubPage = pathname.split("/").pop() !== apartment.id;

    return (
        <div className="view--apartment-details">
            <Heading type="main">
                <div>
                    <Link to={`/housing-companies/${apartment.links.housing_company.id}`}>
                        <span className="name">
                            {apartment.links.housing_company.display_name} {isApartmentSubPage}
                        </span>
                    </Link>
                    {isApartmentSubPage ? (
                        <Link
                            to={`/housing-companies/${apartment.links.housing_company.id}/apartments/${apartment.id}`}
                        >
                            <span className="address">{apartment && formatAddress(apartment.address)}</span>
                        </Link>
                    ) : (
                        <span className="address">{apartment && formatAddress(apartment.address)}</span>
                    )}
                    <StatusLabel>{getApartmentStateLabel(apartment.state)}</StatusLabel>
                    {apartment.sell_by_date ? (
                        <StatusLabel
                            className="conditions-of-sale-status"
                            iconLeft={<IconLock />}
                        />
                    ) : null}
                </div>
                {showEditButton ? <EditButton /> : null}
            </Heading>
        </div>
    );
};

export default ApartmentHeader;
