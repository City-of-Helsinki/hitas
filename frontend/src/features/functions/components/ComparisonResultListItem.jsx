import {Link} from "react-router-dom";
import {formatDate} from "../../../common/utils";

const ComparisonResultListItem = ({company}) => (
    <Link to={`/housing-companies/${company.id}`}>
        <li className="results-list__item">
            <div className="name">{company.display_name}</div>
            <div className="address">
                {company.address.street_address}
                <br />
                {company.address.postal_code}, {company.address.city}
            </div>
            <div className="date">{formatDate(company.completion_date)}</div>
        </li>
    </Link>
);

export default ComparisonResultListItem;
