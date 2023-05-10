import {Button} from "hds-react";
import {useState} from "react";
import {Link} from "react-router-dom";
import {downloadCompanyRegulationLetter} from "../../../app/services";
import {formatDate} from "../../../common/utils";

const ComparisonResultListItem = ({company}) => {
    const [isClicked, setIsClicked] = useState(false);
    const handleClick = () => {
        downloadCompanyRegulationLetter(company);
        setIsClicked(true);
    };
    return (
        <li className="results-list__item">
            <Link to={`/housing-companies/${company.id}`}>
                <div className="name">{company.display_name}</div>
                <div className="address">
                    {company.address.street_address}
                    <br />
                    {company.address.postal_code}, {company.address.city}
                </div>
                <div className="date">{formatDate(company.completion_date)}</div>
                <div className="property-manager">{company.property_manager.email}</div>
            </Link>
            <Button
                theme="black"
                onClick={handleClick}
                variant={isClicked ? "secondary" : "primary"}
                className="download-button"
            >
                Lataa tiedote
            </Button>
        </li>
    );
};

export default ComparisonResultListItem;
