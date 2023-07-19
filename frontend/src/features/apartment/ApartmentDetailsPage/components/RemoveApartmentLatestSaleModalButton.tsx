import {IconTrash} from "hds-react";
import {useContext, useState} from "react";
import {useDeleteSaleMutation} from "../../../../app/services";
import {DeleteButton, GenericActionModal} from "../../../../common/components";
import {formatDate, formatMoney, hdsToast} from "../../../../common/utils";
import {ApartmentViewContext} from "../../components/ApartmentViewContextProvider";

const RemoveApartmentLatestSaleModalButton = () => {
    const {housingCompany, apartment} = useContext(ApartmentViewContext);
    if (!apartment) throw new Error("Apartment not found");

    if (!apartment.prices.current_sale_id || !apartment.prices.latest_purchase_date) return null;

    const [isModalOpen, setIsModalOpen] = useState(false);
    const closeModal = () => setIsModalOpen(false);

    const [removeSale, {isLoading}] = useDeleteSaleMutation();

    const handleRemoveSaleButtonClick = () => {
        removeSale({
            housingCompanyId: housingCompany.id,
            apartmentId: apartment.id,
            saleId: apartment.prices.current_sale_id as string,
        })
            .unwrap()
            .then(() => {
                hdsToast.success("Viimeisin kauppa peruttu onnistuneesti");
            })
            .catch((e) => {
                hdsToast.error("Viimeisimmän kaupan peruminen epäonnistui");
                // eslint-disable-next-line no-console
                console.warn(e);
            });
        setIsModalOpen(false);
    };

    const getLatestSaleDescription = () => {
        const price = apartment.prices.latest_sale_purchase_price ?? apartment.prices.first_sale_purchase_price;
        return `(${formatDate(apartment.prices.latest_purchase_date)}, ${formatMoney(price)})`;
    };

    return (
        <>
            <DeleteButton
                onClick={() => setIsModalOpen(true)}
                isLoading={isLoading}
                buttonText="Peru kauppa"
                variant="secondary"
                size="small"
                className="delete-sale-button"
                disabled={!apartment.prices.current_sale_id || !apartment.prices.latest_purchase_date}
            />

            <GenericActionModal
                title="Asunnon viimeisimmän kaupan peruminen"
                modalIcon={<IconTrash />}
                isModalOpen={isModalOpen}
                closeModal={closeModal}
                confirmButton={
                    <DeleteButton
                        onClick={handleRemoveSaleButtonClick}
                        isLoading={isLoading}
                        buttonText="Vahvista kaupan peruminen"
                    />
                }
                danger
            >
                <p>
                    Haluatko varmasti perua viimeisimmän kaupan
                    <br />
                    {getLatestSaleDescription()}?
                </p>
            </GenericActionModal>
        </>
    );
};

export default RemoveApartmentLatestSaleModalButton;
