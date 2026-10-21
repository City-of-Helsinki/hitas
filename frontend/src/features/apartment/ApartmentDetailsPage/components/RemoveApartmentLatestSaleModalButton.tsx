import {ButtonSize, ButtonVariant, IconTrash} from "hds-react";
import {useContext, useState} from "react";
import {DeleteButton, GenericActionModal} from "../../../../common/components";
import {useDeleteSaleMutation} from "../../../../common/services";
import {formatDate, formatMoney, hdsToast} from "../../../../common/utils";
import {ApartmentViewContext} from "../../components/ApartmentViewContextProvider";

const RemoveApartmentLatestSaleModalButton = () => {
    const {housingCompany, apartment} = useContext(ApartmentViewContext);
    if (!apartment) throw new Error("Apartment not found");

    const [isModalOpen, setIsModalOpen] = useState(false);
    const closeModal = () => setIsModalOpen(false);

    const [removeSale, {isLoading}] = useDeleteSaleMutation();

    if (!apartment.prices.current_sale_id) return null;

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
                variant={ButtonVariant.Secondary}
                size={ButtonSize.Small}
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
