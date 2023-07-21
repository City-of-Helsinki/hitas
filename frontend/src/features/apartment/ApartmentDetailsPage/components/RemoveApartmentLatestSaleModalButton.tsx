import {IconTrash} from "hds-react";
import {useContext, useState} from "react";
import {DeleteButton, GenericActionModal} from "../../../../common/components";
import {useDeleteSaleMutation} from "../../../../common/services";
import {formatDate, formatMoney, hdsToast} from "../../../../common/utils";
import {ApartmentViewContext} from "../../components/ApartmentViewContextProvider";

const canApartmentSaleBeDeleted = (apartment) => {
    // No sale to remove
    if (!apartment.prices.current_sale_id) return false;

    // Sale can always be removed if apartment is not complete
    if (!apartment.completion_date) return true;

    const today = new Date();
    const completionDate = new Date(apartment.completion_date);

    // First sale can be removed before apartment is completed
    if (today < completionDate) return true;

    // First sale can be removed within 3 months after completion date
    if (!apartment.prices.latest_purchase_date && apartment.prices.first_purchase_date) {
        return completionDate < new Date(today.setMonth(today.getMonth() - 3));
    }

    // Latest sale can be removed within 3 months of sale date
    if (apartment.prices.latest_purchase_date) {
        return new Date(apartment.prices.latest_purchase_date) < new Date(today.setMonth(today.getMonth() - 3));
    }

    return false;
};

const RemoveApartmentLatestSaleModalButton = () => {
    const {housingCompany, apartment} = useContext(ApartmentViewContext);
    if (!apartment) throw new Error("Apartment not found");

    const [isModalOpen, setIsModalOpen] = useState(false);
    const closeModal = () => setIsModalOpen(false);

    const [removeSale, {isLoading}] = useDeleteSaleMutation();

    const canSaleBeDeleted = canApartmentSaleBeDeleted(apartment);
    if (!canSaleBeDeleted) return null;

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
        const date = apartment.prices.latest_purchase_date ?? apartment.prices.first_purchase_date;
        const price = apartment.prices.latest_sale_purchase_price ?? apartment.prices.first_sale_purchase_price;
        return `(${formatDate(date)}, ${formatMoney(price)})`;
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
                disabled={!apartment.prices.current_sale_id}
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
