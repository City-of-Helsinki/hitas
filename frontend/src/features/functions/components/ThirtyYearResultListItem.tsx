import {Button, IconDocument, IconLockOpen} from "hds-react";
import {useState} from "react";
import {Link} from "react-router-dom";
import {downloadCompanyRegulationLetter} from "../../../app/services";
import ConfirmDialogModal from "../../../common/components/ConfirmDialogModal";
import {formatDate, hdsToast} from "../../../common/utils";

const ThirtyYearResultListItem = ({company, category}) => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const handleClick = () => {
        downloadCompanyRegulationLetter(company);
    };
    const handleFree = () => {
        console.log(`Action to free ${company.display_name} from regulation`);
        hdsToast.success(`Yhtiön ${company.display_name} manuaalinen vapautus onnistui.`);
    };
    return (
        <li className="results-list__item">
            <Link
                to={`/housing-companies/${company.id}`}
                target="_blank"
            >
                <div className="name">{company.display_name}</div>
                <div className="address">
                    {company.address.street_address}
                    <br />
                    {company.address.postal_code}, {company.address.city}
                </div>
            </Link>
            <div className="date">{formatDate(company.completion_date)}</div>
            <div className="property-manager">{company.property_manager.email}</div>
            <div className="buttons">
                {category !== "freed" && (
                    <Button
                        theme="black"
                        onClick={() => setIsModalOpen(true)}
                        iconLeft={<IconLockOpen />}
                    >
                        Vapauta
                    </Button>
                )}
                <Button
                    theme="black"
                    onClick={handleClick}
                    variant={company.letter_fetched ? "secondary" : "primary"}
                    className="download-button"
                    iconLeft={<IconDocument />}
                >
                    Lataa tiedote
                </Button>
            </div>
            <ConfirmDialogModal
                modalHeader={`Vapauta ${company.display_name}?`}
                modalText={`Olet manuaalisesti vapauttamassa yhtiötä (esim tontit-yksikön päätöksestä). Haluatko varmasti, että ${company.display_name} vapautetaan sääntelyn piiristä?`}
                isVisible={isModalOpen}
                setIsVisible={setIsModalOpen}
                buttonText="Vapauta"
                confirmAction={handleFree}
                cancelAction={() => setIsModalOpen(false)}
            />
        </li>
    );
};

export default ThirtyYearResultListItem;
