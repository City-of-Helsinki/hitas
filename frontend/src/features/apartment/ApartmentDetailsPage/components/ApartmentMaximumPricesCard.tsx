import {Button, Card, IconDownload} from "hds-react";
import {useContext, useRef, useState} from "react";
import {useForm} from "react-hook-form";
import {Link} from "react-router-dom";
import {DownloadButton, GenericActionModal} from "../../../../common/components";
import {DateInput, FormProviderForm, SaveFormButton, TextAreaInput} from "../../../../common/components/forms";
import {
    IApartmentConfirmedMaximumPrice,
    IApartmentDetails,
    IApartmentUnconfirmedMaximumPrice,
    IHousingCompanyDetails,
} from "../../../../common/schemas";
import {
    downloadApartmentMaximumPricePDF,
    downloadApartmentUnconfirmedMaximumPricePDF,
} from "../../../../common/services";
import {formatDate, formatMoney, getApartmentUnconfirmedPrices, today} from "../../../../common/utils";
import {ApartmentViewContext} from "../../components/ApartmentViewContextProvider";

interface UnconfirmedPriceRowProps {
    label: string;
    unconfirmedPrice: IApartmentUnconfirmedMaximumPrice;
}

const UnconfirmedPriceRow = ({label, unconfirmedPrice}: UnconfirmedPriceRowProps) => {
    return (
        <div className={`price${unconfirmedPrice.maximum ? " price--current-top" : ""}`}>
            <span className="basis">{label}</span>
            <span className="amount">
                <span className="value">{formatMoney(unconfirmedPrice.value)}</span>
            </span>
        </div>
    );
};
const ConfirmedPriceDetails = ({confirmed}: {confirmed: IApartmentConfirmedMaximumPrice | null}) => {
    if (confirmed === null) return <p className="confirmed-price">-</p>;
    return (
        <>
            <div className="confirmed-price">{formatMoney(confirmed.maximum_price)}</div>
            <div className="confirmed-price__date">Vahvistettu: {formatDate(confirmed.confirmed_at.split("T")[0])}</div>
            <div className="confirmed-price__date">
                Voimassa:{" "}
                {new Date() <= new Date(confirmed.valid.valid_until) ? (
                    `${formatDate(confirmed.valid.valid_until)} asti`
                ) : (
                    <span>
                        <span className="invalid">{formatDate(confirmed.valid.valid_until)} - ei voimassa</span>
                    </span>
                )}
            </div>
        </>
    );
};
const UnconfirmedPricesDownloadModalButton = () => {
    const {housingCompany, apartment} = useContext(ApartmentViewContext);
    if (!apartment) throw new Error("Apartment not found");

    const [isModalOpen, setIsModalOpen] = useState(false);
    const closeModal = () => setIsModalOpen(false);

    const formRef = useRef<HTMLFormElement>(null);
    const formObject = useForm({
        defaultValues: {calculation_date: today(), request_date: today(), additional_info: ""},
    });

    const onSubmit = () => {
        downloadApartmentUnconfirmedMaximumPricePDF(
            apartment,
            formObject.getValues("request_date"),
            formObject.getValues("additional_info"),
            formObject.getValues("calculation_date")
        );
        closeModal();
    };

    const unconfirmedPrices = getApartmentUnconfirmedPrices(apartment);

    return (
        <>
            <DownloadButton
                buttonText="Lataa Hinta-arvio"
                onClick={() => setIsModalOpen(true)}
                size="small"
                disabled={
                    // Button should be disabled if any of the price calculations are missing
                    !(
                        unconfirmedPrices.market_price_index.value &&
                        unconfirmedPrices.construction_price_index.value &&
                        unconfirmedPrices.surface_area_price_ceiling.value
                    ) ||
                    housingCompany.regulation_status !== "regulated" ||
                    housingCompany.hitas_type === "half_hitas"
                }
            />
            <GenericActionModal
                id="unconfirmed-prices-download-modal"
                title="Lataa enimmäishinta-arvio"
                modalIcon={<IconDownload />}
                isModalOpen={isModalOpen}
                closeModal={closeModal}
                confirmButton={
                    <SaveFormButton
                        formRef={formRef}
                        buttonText="Lataa enimmäishinta-arvio"
                    />
                }
            >
                <FormProviderForm
                    formObject={formObject}
                    formRef={formRef}
                    onSubmit={onSubmit}
                >
                    <DateInput
                        name="calculation_date"
                        label="Hinta-arvion päivämäärä"
                        maxDate={new Date()}
                        tooltipText="Päivämäärä jolle hinta-arvio lasketaan."
                        required
                    />
                    <TextAreaInput
                        name="additional_info"
                        label="Lisätietoja"
                        tooltipText="Lisätietokenttään kirjoitetaan jos laskelmassa on jotain erityistä mitä osakkaan on syytä tietää. Kentän teksti lisätään hinta-arviotulosteeseen."
                    />
                    <DateInput
                        name="request_date"
                        label="Pyynnön vastaanottamispäivä"
                        maxDate={new Date()}
                        tooltipText="Päivämäärä jolloin hinta-arvio pyyntö on vastaanotettu."
                        required
                    />
                </FormProviderForm>
            </GenericActionModal>
        </>
    );
};
const MaximumPriceDownloadModalButton = () => {
    const {housingCompany, apartment} = useContext(ApartmentViewContext);
    if (!apartment) throw new Error("Apartment not found");

    const [isModalOpen, setIsModalOpen] = useState(false);
    const closeModal = () => setIsModalOpen(false);

    const formRef = useRef<HTMLFormElement>(null);
    const formObject = useForm({
        defaultValues: {request_date: today(), additional_info: ""},
    });

    const onSubmit = () => {
        downloadApartmentMaximumPricePDF(apartment, formObject.getValues("request_date"));
        setIsModalOpen(false);
    };

    return (
        <>
            <DownloadButton
                buttonText="Lataa enimmäishintalaskelma"
                onClick={() => setIsModalOpen(true)}
                size="small"
                disabled={
                    !apartment.prices.maximum_prices.confirmed?.id ||
                    housingCompany.regulation_status !== "regulated" ||
                    housingCompany.hitas_type === "half_hitas"
                }
            />
            <GenericActionModal
                title="Lataa enimmäishintalaskelma"
                modalIcon={<IconDownload />}
                isModalOpen={isModalOpen}
                closeModal={closeModal}
                confirmButton={
                    <SaveFormButton
                        formRef={formRef}
                        buttonText="Lataa enimmäishintalaskelma"
                    />
                }
            >
                <FormProviderForm
                    formObject={formObject}
                    formRef={formRef}
                    onSubmit={onSubmit}
                >
                    <DateInput
                        name="request_date"
                        label="Pyynnön vastaanottamispäivä"
                        maxDate={new Date()}
                        tooltipText="Päivämäärä, jolloin enimmäishintalaskelma pyyntö on vastaanotettu."
                        required
                    />
                </FormProviderForm>
            </GenericActionModal>
        </>
    );
};

const ApartmentMaximumPricesCard = ({
    apartment,
    housingCompany,
}: {
    apartment: IApartmentDetails;
    housingCompany: IHousingCompanyDetails;
}) => {
    const unconfirmedPrices = getApartmentUnconfirmedPrices(apartment);

    return (
        <Card>
            <label className="card-heading">Vahvistamaton enimmäishinta</label>
            <div className="unconfirmed-prices">
                <UnconfirmedPriceRow
                    label="Markkinahintaindeksi"
                    unconfirmedPrice={unconfirmedPrices.market_price_index}
                />
                <UnconfirmedPriceRow
                    label="Rakennuskustannusindeksi"
                    unconfirmedPrice={unconfirmedPrices.construction_price_index}
                />
                <UnconfirmedPriceRow
                    label="Rajaneliöhinta"
                    unconfirmedPrice={unconfirmedPrices.surface_area_price_ceiling}
                />
                <div className="align-content-right">
                    <UnconfirmedPricesDownloadModalButton />
                </div>
            </div>

            <label className="card-heading">Vahvistettu enimmäishinta</label>
            <ConfirmedPriceDetails confirmed={apartment.prices.maximum_prices.confirmed} />

            <div className="align-content-right">
                <MaximumPriceDownloadModalButton />
                <Link to="max-price">
                    <Button
                        theme="black"
                        size="small"
                        disabled={
                            !housingCompany.completion_date ||
                            housingCompany.regulation_status !== "regulated" ||
                            housingCompany.hitas_type === "half_hitas" ||
                            !apartment.prices.first_purchase_date
                        }
                    >
                        Vahvista
                    </Button>
                </Link>
            </div>
        </Card>
    );
};

export default ApartmentMaximumPricesCard;
