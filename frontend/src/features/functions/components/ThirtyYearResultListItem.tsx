import {Button, IconDocument, IconLockOpen} from "hds-react";
import {useState} from "react";
import {Link} from "react-router-dom";
import {
    downloadCompanyRegulationLetter,
    useGetHousingCompanyDetailQuery,
    useSaveHousingCompanyMutation,
} from "../../../app/services";
import ConfirmDialogModal from "../../../common/components/ConfirmDialogModal";
import {formatDate, hdsToast} from "../../../common/utils";

const ThirtyYearResultListItem = ({company, category}) => {
    const [hasBeenFreed, setHasBeenFreed] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [saveHousingCompany] = useSaveHousingCompanyMutation();
    const {data: housingCompany, isLoading, error} = useGetHousingCompanyDetailQuery(company.id);
    const handleClickDownload = () => {
        downloadCompanyRegulationLetter(company);
    };
    const handleFree = () => {
        housingCompany &&
            !isLoading &&
            !error &&
            saveHousingCompany({
                data: {
                    ...housingCompany,
                    regulation_status: "released_by_plot_department",
                },
                id: company.id,
            })
                .then(() => {
                    setHasBeenFreed(true);
                    hdsToast.success(`${company.display_name} vapautettu onnistuneesti.`);
                })
                .catch((error) => {
                    hdsToast.error(`${company.display_name} vapautus epäonnistui.`);
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
                        variant={hasBeenFreed ? "secondary" : "primary"}
                        onClick={() => setIsModalOpen(true)}
                        iconLeft={<IconLockOpen />}
                        disabled={hasBeenFreed}
                    >
                        {hasBeenFreed ? "Vapautettu" : "Vapauta"}
                    </Button>
                )}
                {!hasBeenFreed && (
                    <Button
                        theme="black"
                        onClick={handleClickDownload}
                        variant={company.letter_fetched ? "secondary" : "primary"}
                        className="download-button"
                        iconLeft={<IconDocument />}
                    >
                        Lataa tiedote
                    </Button>
                )}
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
