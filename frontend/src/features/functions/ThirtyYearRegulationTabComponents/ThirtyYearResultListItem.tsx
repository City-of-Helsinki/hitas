import {Button, IconLockOpen} from "hds-react";
import {useState} from "react";
import {Link} from "react-router-dom";
import {ConfirmDialogModal, DownloadButton} from "../../../common/components";
import {useDownloadThirtyYearRegulationLetterMutation, usePatchHousingCompanyMutation} from "../../../common/services";

import {formatDate, hdsToast} from "../../../common/utils";

const ThirtyYearResultListItem = ({housingCompany, calculationDate, category}) => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [patchHousingCompany] = usePatchHousingCompanyMutation();
    const [downloadPDFFile] = useDownloadThirtyYearRegulationLetterMutation();
    const isHousingCompanyReleased = housingCompany.current_regulation_status !== "regulated";

    const handleClickDownloadPDFButton = () => {
        downloadPDFFile({id: housingCompany.id, calculationDate: calculationDate});
    };

    const handleFreeHousingCompanyFromRegulation = () => {
        patchHousingCompany({
            housingCompanyId: housingCompany.id,
            data: {regulation_status: "released_by_plot_department"},
        })
            .then(() => {
                hdsToast.success(`${housingCompany.display_name} vapautettu onnistuneesti.`);
            })
            .catch((error) => {
                hdsToast.error(`${housingCompany.display_name} vapautus epäonnistui.`);
                // eslint-disable-next-line no-console
                console.warn("Caught error:", error);
            });
        setIsModalOpen(false);
    };

    return (
        <li className="results-list__item">
            <div className="company-info">
                <Link
                    to={`/housing-companies/${housingCompany.id}`}
                    target="_blank"
                >
                    <div className="name">{housingCompany.display_name}</div>
                    <div className="address">
                        {housingCompany.address.street_address}
                        <br />
                        {housingCompany.address.postal_code}, {housingCompany.address.city}
                    </div>
                </Link>
                <div className="date">{formatDate(housingCompany.completion_date)}</div>
                <div className="property-manager">{housingCompany.property_manager.email}</div>
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
                {housingCompany.current_regulation_status !== "released_by_plot_department" && (
                    <DownloadButton
                        buttonText="Lataa tiedote"
                        onClick={handleClickDownloadPDFButton}
                        variant={housingCompany.letter_fetched ? "secondary" : "primary"}
                    />
                )}
            </div>
            <ConfirmDialogModal
                modalHeader={`Vapauta ${housingCompany.display_name}?`}
                modalText={`Olet manuaalisesti vapauttamassa yhtiötä (esim tontit-yksikön päätöksestä). Haluatko
                    varmasti, että ${housingCompany.display_name} vapautetaan sääntelyn piiristä?`}
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
