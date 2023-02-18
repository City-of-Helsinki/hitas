import {StatusLabel} from "hds-react";
import {Link} from "react-router-dom";

import {EditButton, Heading} from "../../../common/components";
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
                    <StatusLabel>{apartment.state}</StatusLabel>
                </Link>
                {showEditButton ? <EditButton state={{apartment: apartment}} /> : null}
            </Heading>
        </div>
    );
};

export default ApartmentHeader;
