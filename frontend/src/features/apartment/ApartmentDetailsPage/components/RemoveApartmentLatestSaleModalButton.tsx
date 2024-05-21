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

    // First sale can be removed before apartment is completed (Completion date is in the future)
    if (today < completionDate) return true;

    const oneYearAgo = new Date(today);
    oneYearAgo.setFullYear(today.getFullYear() - 1);

    const comparisonDate = [
        completionDate,
        new Date(apartment.prices.first_purchase_date),
        new Date(apartment.prices.latest_purchase_date),
    ]
        .sort((a, b) => a.getTime() - b.getTime())
        .reverse()[0];

    if (comparisonDate > oneYearAgo) return true;

    // Apartment sale can be removed if there are conditions of sale, and this is the new apartment
    if (apartment.conditions_of_sale?.length > 0) {
        // Frontend doesn't know which apartment is the new one, so we do some guesswork
        // If the apartment has been resold, it's never the new one
        if (apartment.prices.latest_purchase_date) return false;

        // If the comparison date is within a year of today, it's most likely the new apartment
        if (comparisonDate > oneYearAgo) return true;
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
