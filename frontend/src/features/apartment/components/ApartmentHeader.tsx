import {IconLock, StatusLabel} from "hds-react";
import {Link} from "react-router-dom";

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
    return (
        <div className="view--apartment-details">
            <Heading type="main">
                <Link to={`/housing-companies/${apartment.links.housing_company.id}`}>
                    <span className="name">{apartment.links.housing_company.display_name}</span>
                    <span className="address">{apartment && formatAddress(apartment.address)}</span>
                    <StatusLabel>{getApartmentStateLabel(apartment.state)}</StatusLabel>
                    {apartment.sell_by_date ? (
                        <StatusLabel
                            className="conditions-of-sale-lock"
                            iconLeft={<IconLock />}
                        />
                    ) : null}
                </Link>
                {showEditButton ? <EditButton state={{apartment: apartment}} /> : null}
            </Heading>
        </div>
    );
};

export default ApartmentHeader;
