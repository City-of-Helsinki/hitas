import {Button, IconLockOpen} from "hds-react";
import {useState} from "react";
import {Link} from "react-router-dom";
import {ConfirmDialogModal, DownloadButton} from "../../../common/components";
import {
    useDownloadThirtyYearRegulationLetterMutation,
    useReleaseHousingCompanyFromRegulationMutation,
} from "../../../common/services";

import {formatDate, hdsToast} from "../../../common/utils";

const ThirtyYearResultListItem = ({company, calculationDate, category}) => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [releaseHousingCompany] = useReleaseHousingCompanyFromRegulationMutation();
    const [downloadPDFFile] = useDownloadThirtyYearRegulationLetterMutation();
    const isHousingCompanyReleased = company.current_regulation_status !== "regulated";

    const handleClickDownloadPDFButton = () => {
        downloadPDFFile({id: company.id, calculationDate: calculationDate});
    };

    const handleFreeHousingCompanyFromRegulation = () => {
        releaseHousingCompany({
            housingCompanyId: company.id,
            calculationDate: calculationDate,
        })
            .then(() => {
                hdsToast.success(`${company.display_name} vapautettu onnistuneesti.`);
            })
            .catch((error) => {
                hdsToast.error(`${company.display_name} vapautus epäonnistui.`);
                // eslint-disable-next-line no-console
                console.warn("Caught error:", error);
            });
        setIsModalOpen(false);
    };

    return (
        <li className="results-list__item">
            <div className="company-info">
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
            </div>
            <div className="buttons">
                {category !== "freed" && (
                    <Button
                        className="manual-free-button"
                        theme="black"
                        variant={isHousingCompanyReleased ? "secondary" : "primary"}
                        onClick={() => setIsModalOpen(true)}
                        iconLeft={<IconLockOpen />}
                        disabled={isHousingCompanyReleased}
                    >
                        {isHousingCompanyReleased ? "Vapautettu" : "Vapauta"}
                    </Button>
                )}
                {company.current_regulation_status !== "released_by_plot_department" && (
                    <DownloadButton
                        buttonText="Lataa tiedote"
                        downloadFn={handleClickDownloadPDFButton}
                        variant={company.letter_fetched ? "secondary" : "primary"}
                    />
                )}
            </div>
            <ConfirmDialogModal
                modalHeader={`Vapauta ${company.display_name}?`}
                modalText={`Olet manuaalisesti vapauttamassa yhtiötä (esim tontit-yksikön päätöksestä). Haluatko
                    varmasti, että ${company.display_name} vapautetaan sääntelyn piiristä?`}
                isVisible={isModalOpen}
                setIsVisible={setIsModalOpen}
                buttonText="Vapauta"
                confirmAction={handleFreeHousingCompanyFromRegulation}
                cancelAction={() => setIsModalOpen(false)}
            />
        </li>
    );
};

export default ThirtyYearResultListItem;
