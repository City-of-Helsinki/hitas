import {useRef, useState} from "react";

import {Button, Card, Dialog, IconDownload, IconGlyphEuro, IconLock, Tabs} from "hds-react";
import {Link, useParams} from "react-router-dom";

import {useForm} from "react-hook-form";
import {
    downloadApartmentMaximumPricePDF,
    downloadApartmentUnconfirmedMaximumPricePDF,
    useGetApartmentDetailQuery,
    useGetHousingCompanyDetailQuery,
} from "../../app/services";
import {DetailField, Divider, ImprovementsTable, QueryStateHandler} from "../../common/components";
import {DateInput, TextAreaInput} from "../../common/components/form";
import {
    IApartmentConditionOfSale,
    IApartmentConfirmedMaximumPrice,
    IApartmentDetails,
    IApartmentUnconfirmedMaximumPrice,
    IHousingCompanyDetails,
    IOwnership,
} from "../../common/schemas";
import {formatAddress, formatDate, formatMoney, hdsToast, today} from "../../common/utils";
import ApartmentHeader from "./components/ApartmentHeader";
import ConditionsOfSaleStatus from "./components/ConditionsOfSaleStatus";

const SingleApartmentConditionOfSale = ({conditionsOfSale}: {conditionsOfSale: IApartmentConditionOfSale[]}) => {
    return (
        <li>
            <h3>
                {conditionsOfSale[0].owner.name} ({conditionsOfSale[0].owner.identifier})
            </h3>
            <ul>
                {conditionsOfSale.map((cos) => (
                    <li
                        key={cos.id}
                        className={cos.fulfilled ? "resolved" : "unresolved"}
                    >
                        <Link
                            to={`/housing-companies/${cos.apartment.housing_company.id}/apartments/${cos.apartment.id}`}
                        >
                            <ConditionsOfSaleStatus conditionOfSale={cos} />
                            <span className="address">{formatAddress(cos.apartment.address)}</span>
                        </Link>
                    </li>
                ))}
            </ul>
        </li>
    );
};

const ApartmentConditionsOfSaleCard = ({apartment}: {apartment: IApartmentDetails}) => {
    const conditionsOfSale = apartment.conditions_of_sale;
    // Create a dict with owner id as key, and all of their conditions of sale in a list as value
    interface IGroupedConditionsOfSale {
        [ownerId: string]: IApartmentConditionOfSale[];
    }
    const groupedConditionsOfSale: IGroupedConditionsOfSale = conditionsOfSale.reduce((acc, obj) => {
        if (obj.owner.id in acc) {
            acc[obj.owner.id].push(obj);
        } else {
            acc[obj.owner.id] = [obj];
        }
        return acc;
    }, {});
    // Order owners with unfulfilled conditions of sale first.
    // When owners have the same amount of unfulfilled conditions of sale, owners with more total COS are last.
    const sortedKeys = Object.keys(groupedConditionsOfSale).sort((a, b) => {
        const diff =
            groupedConditionsOfSale[b].filter((cos) => !cos.fulfilled).length -
            groupedConditionsOfSale[a].filter((cos) => !cos.fulfilled).length;
        if (diff !== 0) return diff;
        return groupedConditionsOfSale[a].length - groupedConditionsOfSale[b].length;
    });

    const ApartmentSalesPageLinkButton = () => {
        // If apartment has been sold for the first time, and it's still not completed, it can not be re-sold
        if (!apartment.completion_date && apartment.prices.first_purchase_date) {
            return (
                <Button
                    theme="black"
                    iconLeft={<IconGlyphEuro />}
                    onClick={() => hdsToast.error("Valmistumatonta asuntoa ei voida jälleenmyydä.")}
                >
                    Kauppatapahtuma
                </Button>
            );
        } else {
            return (
                <Link to="sales">
                    <Button
                        theme="black"
                        iconLeft={<IconGlyphEuro />}
                    >
                        Kauppatapahtuma
                    </Button>
                </Link>
            );
        }
    };

    return (
        <Card>
            <div className="row row--buttons">
                <ApartmentSalesPageLinkButton />
                <Link to="conditions-of-sale">
                    <Button
                        theme="black"
                        iconLeft={<IconLock />}
                        disabled={!apartment.ownerships.length}
                    >
                        Muokkaa myyntiehtoja
                    </Button>
                </Link>
            </div>
            <label className="card-heading card-heading--conditions-of-sale">Myyntiehdot</label>
            {Object.keys(groupedConditionsOfSale).length ? (
                <ul>
                    {sortedKeys.map((ownerId) => (
                        <SingleApartmentConditionOfSale
                            key={ownerId}
                            conditionsOfSale={
                                // Sort owners conditions of sale by unfulfilled first
                                groupedConditionsOfSale[ownerId].sort((a, b) =>
                                    !!a.fulfilled === !!b.fulfilled ? 0 : a.fulfilled ? 1 : -1
                                )
                            }
                        />
                    ))}
                </ul>
            ) : (
                <span className="no-conditions">Ei myyntiehtoja.</span>
            )}
        </Card>
    );
};

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

const ConfirmedPriceDetails = ({confirmed}: {confirmed: IApartmentConfirmedMaximumPrice}) => {
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

interface DownloadModalProps {
    apartment: IApartmentDetails;
    isVisible: boolean;
    setIsVisible;
}

const UnconfirmedPricesDownloadModal = ({apartment, isVisible, setIsVisible}: DownloadModalProps) => {
    const formRef = useRef<HTMLFormElement>(null);
    const downloadForm = useForm({defaultValues: {request_date: today(), additional_info: ""}});
    const {handleSubmit} = downloadForm;
    const handleDownloadButtonClick = () => {
        formRef.current && formRef.current.dispatchEvent(new Event("submit", {cancelable: true, bubbles: true}));
    };
    const onSubmit = () => {
        downloadApartmentUnconfirmedMaximumPricePDF(
            apartment,
            downloadForm.getValues("additional_info"),
            downloadForm.getValues("request_date")
        );
        setIsVisible(false);
    };

    return (
        <Dialog
            id="unconfirmed-prices-download-modal"
            closeButtonLabelText=""
            aria-labelledby=""
            isOpen={isVisible}
            close={() => setIsVisible(false)}
            boxShadow
        >
            <Dialog.Header
                id="unconfirmed-prices-download-modal__header"
                title="Lataa enimmäishinta-arvio"
            />
            <Dialog.Content>
                <form
                    ref={formRef}
                    onSubmit={handleSubmit(onSubmit)}
                >
                    <TextAreaInput
                        name="additional_info"
                        label="Lisätietoja"
                        formObject={downloadForm}
                        tooltipText="Lisätietokenttään kirjoitetaan, jos laskelmassa on jotain erityistä, mitä osakkaan on syytä tietää. Kentän teksti lisätään tulostettavaan hinta-arvio PDF:ään."
                    />
                    <DateInput
                        name="request_date"
                        label="Pyynnön vastaanottamispäivä"
                        formObject={downloadForm}
                        maxDate={new Date()}
                        tooltipText="Päivämäärä, jolloin hinta-arvio pyyntö on vastaanotettu."
                        required
                    />
                </form>
            </Dialog.Content>
            <Dialog.ActionButtons>
                <Button
                    onClick={() => setIsVisible(false)}
                    variant="secondary"
                    theme="black"
                    size="small"
                >
                    Sulje
                </Button>
                <Button
                    theme="black"
                    size="small"
                    iconLeft={<IconDownload />}
                    onClick={() => handleDownloadButtonClick()}
                >
                    Lataa Hinta-arvio
                </Button>
            </Dialog.ActionButtons>
        </Dialog>
    );
};

const MaximumPriceDownloadModal = ({apartment, isVisible, setIsVisible}: DownloadModalProps) => {
    const formRef = useRef<HTMLFormElement>(null);
    const downloadForm = useForm({defaultValues: {request_date: formatDate(Date()), additional_info: ""}});
    const {handleSubmit} = downloadForm;
    const handleDownloadButtonClick = () => {
        formRef.current && formRef.current.dispatchEvent(new Event("submit", {cancelable: true, bubbles: true}));
    };
    const onSubmit = () => {
        downloadApartmentMaximumPricePDF(apartment, downloadForm.getValues("request_date"));
        setIsVisible(false);
    };

    return (
        <Dialog
            id="maximum-prices-download-modal"
            closeButtonLabelText=""
            aria-labelledby=""
            isOpen={isVisible}
            close={() => setIsVisible(false)}
            boxShadow
        >
            <Dialog.Header
                id="unconfirmed-prices-download-modal__header"
                title="Lataa enimmäishintalaskelma"
            />
            <Dialog.Content>
                <form
                    ref={formRef}
                    onSubmit={handleSubmit(onSubmit)}
                >
                    <DateInput
                        name="request_date"
                        label="Pyynnön vastaanottamispäivä"
                        formObject={downloadForm}
                        maxDate={new Date()}
                        tooltipText="Päivämäärä, jolloin enimmäishintalaskelma pyyntö on vastaanotettu."
                        required
                    />
                </form>
            </Dialog.Content>
            <Dialog.ActionButtons>
                <Button
                    onClick={() => setIsVisible(false)}
                    variant="secondary"
                    theme="black"
                    size="small"
                >
                    Sulje
                </Button>
                <Button
                    theme="black"
                    size="small"
                    iconLeft={<IconDownload />}
                    onClick={() => handleDownloadButtonClick()}
                >
                    Lataa enimmäishintalaskelma
                </Button>
            </Dialog.ActionButtons>
        </Dialog>
    );
};

const ApartmentMaximumPricesCard = ({apartment}: {apartment: IApartmentDetails}) => {
    const isPre2011 = apartment.prices.maximum_prices.unconfirmed.pre_2011 !== null;
    const unconfirmedPrices = isPre2011
        ? apartment.prices.maximum_prices.unconfirmed.pre_2011
        : apartment.prices.maximum_prices.unconfirmed.onwards_2011;
    const [isUnconfirmedMaximumPriceModalVisible, setIsUnconfirmedMaximumPriceModalVisible] = useState(false);
    const [isMaximumPriceModalVisible, setIsMaximumPriceModalVisible] = useState(false);

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
                    <Button
                        theme="black"
                        size="small"
                        variant="secondary"
                        onClick={() => setIsUnconfirmedMaximumPriceModalVisible(true)}
                        disabled={
                            // Button should be disabled if any of the price calculations are missing
                            !(
                                unconfirmedPrices.market_price_index.value &&
                                unconfirmedPrices.construction_price_index.value &&
                                unconfirmedPrices.surface_area_price_ceiling.value
                            )
                        }
                    >
                        Lataa Hinta-arvio
                    </Button>
                </div>
            </div>

            <label className="card-heading">Vahvistettu enimmäishinta</label>
            <ConfirmedPriceDetails confirmed={apartment.prices.maximum_prices.confirmed} />
            <div className="align-content-right">
                <Button
                    theme="black"
                    size="small"
                    variant="secondary"
                    onClick={() => setIsMaximumPriceModalVisible(true)}
                    disabled={
                        !apartment.prices.maximum_prices.confirmed || !apartment.prices.maximum_prices.confirmed.id
                    }
                >
                    Lataa enimmäishintalaskelma
                </Button>
                <Link to="max-price">
                    <Button
                        theme="black"
                        size="small"
                        disabled={!apartment.completion_date}
                    >
                        Vahvista
                    </Button>
                </Link>
            </div>

            <UnconfirmedPricesDownloadModal
                apartment={apartment}
                isVisible={isUnconfirmedMaximumPriceModalVisible}
                setIsVisible={setIsUnconfirmedMaximumPriceModalVisible}
            />
            <MaximumPriceDownloadModal
                apartment={apartment}
                isVisible={isMaximumPriceModalVisible}
                setIsVisible={setIsMaximumPriceModalVisible}
            />
        </Card>
    );
};

const LoadedApartmentDetails = ({
    apartment,
    housingCompany,
}: {
    apartment: IApartmentDetails;
    housingCompany: IHousingCompanyDetails;
}): JSX.Element => {
    return (
        <>
            <ApartmentHeader showEditButton={true} />
            <h2 className="apartment-stats">
                <span className="apartment-stats--number">
                    {apartment.address.stair}
                    {apartment.address.apartment_number}
                </span>
                <span>
                    {apartment.rooms || ""}
                    {apartment.type?.value || ""}
                </span>
                <span>{apartment.surface_area ? apartment.surface_area + "m²" : ""}</span>
                <span>{apartment.address.floor ? apartment.address.floor + ".krs" : ""}</span>
            </h2>
            <div className="apartment-action-cards">
                <ApartmentMaximumPricesCard apartment={apartment} />
                <ApartmentConditionsOfSaleCard apartment={apartment} />
            </div>
            <div className="apartment-details">
                <div className="tab-area">
                    <Tabs>
                        <Tabs.TabList className="tab-list">
                            <Tabs.Tab>Perustiedot</Tabs.Tab>
                            <Tabs.Tab>Dokumentit</Tabs.Tab>
                        </Tabs.TabList>
                        <Tabs.TabPanel>
                            <div className="company-details__tab basic-details">
                                <div className="row">
                                    <DetailField
                                        label="Viimeisin kauppahinta"
                                        value={formatMoney(apartment.prices.latest_sale_purchase_price)}
                                        horizontal
                                    />
                                    <DetailField
                                        label="Hankinta-arvo"
                                        value={formatMoney(apartment.prices.first_sale_acquisition_price)}
                                        horizontal
                                    />
                                    <DetailField
                                        label="Valmistumispäivä"
                                        value={formatDate(apartment.completion_date)}
                                        horizontal
                                    />
                                </div>
                                <Divider size="l" />
                                <div className="columns">
                                    <div className="column">
                                        <div>
                                            <label className="detail-field-label">Omistajat</label>
                                            {apartment.ownerships.map((ownership: IOwnership) => (
                                                <div
                                                    key={ownership.owner.id}
                                                    className="detail-field-value"
                                                >
                                                    {ownership.owner.name} ({ownership.owner.identifier})
                                                    <span> {ownership.percentage}%</span>
                                                </div>
                                            ))}
                                        </div>
                                        <DetailField
                                            label="Isännöitsijä"
                                            value={housingCompany?.property_manager?.name}
                                        />
                                        <DetailField
                                            label="Osakkeet"
                                            value={
                                                apartment.shares
                                                    ? `${apartment.shares.start} - ${apartment.shares.end} (${apartment.shares.total} kpl)`
                                                    : undefined
                                            }
                                        />
                                        <div>
                                            <label className="detail-field-label">Huomioitavaa</label>
                                            <textarea
                                                value={(apartment.notes as string) || ""}
                                                readOnly
                                            />
                                        </div>
                                    </div>
                                    <div className="column">
                                        <DetailField
                                            label="Viimeisin kauppapäivä"
                                            value={formatDate(apartment.prices.latest_purchase_date)}
                                        />

                                        <Divider size="s" />

                                        <DetailField
                                            label="Ensimmäinen kauppapäivä"
                                            value={formatDate(apartment.prices.first_purchase_date)}
                                        />
                                        <DetailField
                                            label="Ensimmäinen Kauppahinta"
                                            value={formatMoney(apartment.prices.first_sale_purchase_price)}
                                        />
                                        <DetailField
                                            label="Ensisijaislaina"
                                            value={formatMoney(
                                                apartment.prices.first_sale_share_of_housing_company_loans
                                            )}
                                        />

                                        <Divider size="s" />

                                        <DetailField
                                            label="Rakennusaikaiset lisätyöt"
                                            value={formatMoney(apartment.prices.construction.additional_work)}
                                        />
                                        <DetailField
                                            label="Rakennusaikaiset korot (6 %)"
                                            value={
                                                apartment.prices.construction.interest
                                                    ? formatMoney(apartment.prices.construction.interest.rate_6)
                                                    : 0
                                            }
                                        />
                                        <DetailField
                                            label="Rakennusaikaiset korot (14 %)"
                                            value={
                                                apartment.prices.construction.interest
                                                    ? formatMoney(apartment.prices.construction.interest.rate_14)
                                                    : 0
                                            }
                                        />
                                        {apartment.prices.construction.loans ? (
                                            <DetailField
                                                label="Rakennusaikaiset lainat"
                                                value={formatMoney(apartment.prices.construction.loans)}
                                            />
                                        ) : null}
                                        {apartment.prices.construction.debt_free_purchase_price ? (
                                            <DetailField
                                                label="Luovutushinta (RA)"
                                                value={formatMoney(
                                                    apartment.prices.construction.debt_free_purchase_price
                                                )}
                                            />
                                        ) : null}

                                        {apartment.prices.catalog_purchase_price ||
                                        apartment.prices.catalog_share_of_housing_company_loans ? (
                                            <>
                                                <Divider size="s" />
                                                <DetailField
                                                    label="Myyntihintaluettelon luovutushinta"
                                                    value={formatMoney(apartment.prices.catalog_purchase_price)}
                                                />
                                                <DetailField
                                                    label="Myyntihintaluettelon ensisijaislaina"
                                                    value={formatMoney(
                                                        apartment.prices.catalog_share_of_housing_company_loans
                                                    )}
                                                />
                                                <DetailField
                                                    label="Myyntihintaluettelon Hankinta-arvo"
                                                    value={formatMoney(apartment.prices.catalog_acquisition_price)}
                                                />
                                            </>
                                        ) : null}
                                    </div>
                                </div>
                            </div>
                        </Tabs.TabPanel>
                        <Tabs.TabPanel>
                            <div className="company-details__tab documents">Dokumentit</div>
                        </Tabs.TabPanel>
                    </Tabs>
                </div>
                <ImprovementsTable
                    data={apartment}
                    title="Asuntokohtaiset parannukset"
                    editableType="apartment"
                />
                <ImprovementsTable
                    data={housingCompany}
                    title="Yhtiökohtaiset parannukset"
                    editableType="housingCompany"
                    editPath={`/housing-companies/${housingCompany.id}/improvements`}
                />
            </div>
        </>
    );
};

const ApartmentDetailsPage = (): JSX.Element => {
    // Load required data and pass it to the child component
    const params = useParams() as {housingCompanyId: string; apartmentId: string};

    const {
        data: housingCompanyData,
        error: housingCompanyError,
        isLoading: isHousingCompanyLoading,
    } = useGetHousingCompanyDetailQuery(params.housingCompanyId);
    const {
        data: apartmentData,
        error: apartmentError,
        isLoading: isApartmentLoading,
    } = useGetApartmentDetailQuery({
        housingCompanyId: params.housingCompanyId,
        apartmentId: params.apartmentId,
    });

    const data = housingCompanyData && apartmentData;
    const error = housingCompanyError || apartmentError;
    const isLoading = isHousingCompanyLoading || isApartmentLoading;

    return (
        <div className="view--apartment-details">
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <LoadedApartmentDetails
                    housingCompany={housingCompanyData as IHousingCompanyDetails}
                    apartment={apartmentData as IApartmentDetails}
                />
            </QueryStateHandler>
        </div>
    );
};

export default ApartmentDetailsPage;
