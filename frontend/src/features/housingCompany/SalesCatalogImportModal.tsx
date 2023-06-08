import {useState} from "react";
import {useCreateSalesCatalogMutation} from "../../app/services";
import {SaveButton, SaveDialogModal} from "../../common/components";
import {ISalesCatalogValidationResponse} from "../../common/schemas";

const SalesCatalogImportModal = ({apartments}: ISalesCatalogValidationResponse) => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [createSalesCatalogApartments, {data: createData, isLoading: isCreating, error: createError}] =
        useCreateSalesCatalogMutation();
    return (
        <div className="sales-catalog-validation-result">
            <div className="sales-catalog-validation-result__headers">
                <header>Porras</header>
                <header>Huoneisto</header>
                <header>Kerros</header>
                <header>Huonelkm</header>
                <header>Huonetyyppi</header>
                <header>Pinta-ala</header>
                <header>Osakkeet</header>
                <header>Kauppahinta</header>
                <header>Ensisijaislaina</header>
                <header>Hankinta-arvo</header>
            </div>
            <ul>
                {apartments.map((apartment, index) => (
                    <li>
                        <div>{apartment.stair}</div>
                        <div>{apartment.apartment_number}</div>
                        <div>{apartment.floor}</div>
                        <div>{apartment.rooms}</div>
                        <div>{(apartment.apartment_type as {value: string}).value}</div>
                        <div>{apartment.surface_area}</div>
                        <div>{`${apartment.share_number_start} - ${apartment.share_number_end}`}</div>
                        <div>{apartment.catalog_purchase_price}</div>
                        <div>{apartment.catalog_primary_loan_amount}</div>
                        <div>{apartment.acquisition_price}</div>
                    </li>
                ))}
            </ul>
            <SaveButton
                isLoading={isCreating}
                onClick={() => createSalesCatalogApartments(apartments)}
            />
            <SaveDialogModal
                title="Tallennetaan excel-tiedostoa"
                data={createData}
                error={createError}
                isLoading={isCreating}
                isVisible={isModalOpen}
                setIsVisible={setIsModalOpen}
            />
        </div>
    );
};

export default SalesCatalogImportModal;
