import React, {useState} from "react";

import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {Button, Checkbox, Dialog, Fieldset, IconAlertCircleFill, LoadingSpinner} from "hds-react";
import {useParams} from "react-router-dom";
import {useImmer} from "use-immer";
import {v4 as uuidv4} from "uuid";

import {
    useGetApartmentDetailQuery,
    useGetApartmentMaximumPriceQuery,
    useSaveApartmentMaximumPriceMutation,
} from "../../app/services";
import {FormInputField, Heading, NavigateBackButton, QueryStateHandler, SaveButton} from "../../common/components";
import OwnershipsList from "../../common/components/OwnershipsList";
import {IApartmentAddress, IApartmentDetails, IApartmentMaximumPrice, IOwnership} from "../../common/models";
import {formatAddress, formatDate, formatIndex, formatMoney} from "../../common/utils";
import MaximumPriceModalContent from "./components/ApartmentMaximumPriceBreakdownModal";

const MaximumPriceModalError = ({error, setIsModalVisible}) => {
    const nonFieldError = ((error as FetchBaseQueryError)?.data as {message?: string})?.message || "";
    return (
        <>
            <Dialog.Content>
                <p>Virhe: {(error as FetchBaseQueryError)?.status}</p>
                <p>{nonFieldError}</p>
            </Dialog.Content>
            <Dialog.ActionButtons>
                <Button
                    onClick={() => setIsModalVisible(false)}
                    variant="secondary"
                    theme="black"
                >
                    Sulje
                </Button>
            </Dialog.ActionButtons>
        </>
    );
};

const LoadedApartmentSalesPage = ({apartment}: {apartment: IApartmentDetails}) => {
    const [isModalVisible, setIsModalVisible] = useState(false);
    const hasValidCalculation = apartment.prices.maximum_prices.confirmed?.valid.is_valid;
    const initialFormData = {
        announcementDate: null,
        dealDate:
            apartment.prices.maximum_prices.confirmed !== null
                ? apartment.prices.maximum_prices.confirmed.calculation_date
                : null,
        dateOfCount:
            apartment.prices.maximum_prices.confirmed !== null
                ? apartment.prices.maximum_prices.confirmed.calculation_date
                : null,
        price: null,
        apartment_share_of_housing_company_loans: hasValidCalculation ? apartment.prices.primary_loan_amount : null,
        mortgageShare: null,
        isExcludedFromStatistics: false,
        index: "",
    };
    const [isExcludedFromStatistics, setIsExcludedFromStatistics] = useState(false);
    const [formData, setFormData] = useImmer(initialFormData);
    const [formOwnershipsList, setFormOwnershipsList] = useImmer<(IOwnership & {key: string})[]>(
        apartment !== undefined ? apartment.ownerships.map((o) => ({...o, key: uuidv4()})) : []
    );
    const [saveMaximumPrice, {data, error, isLoading}] = useSaveApartmentMaximumPriceMutation();
    const {data: maxPriceQuery, error: maxPriceError} = useGetApartmentMaximumPriceQuery({
        housingCompanyId: apartment.links.housing_company.id,
        apartmentId: apartment.id,
        priceId: apartment.prices.maximum_prices.confirmed?.id as string,
    });
    const [maxPrices, setMaxPrices] = useState({
        maxPrice: apartment.prices.maximum_prices.confirmed?.maximum_price,
        maxPricePerSquare: apartment.prices.maximum_prices.confirmed?.maximum_price
            ? apartment.prices.maximum_prices.confirmed?.maximum_price / apartment.surface_area
            : 0,
        debtFreeMaxPrice: apartment.prices.debt_free_purchase_price,
        loanAmount: apartment.prices.primary_loan_amount,
        index: data ? data.index : maxPriceQuery?.index,
    });
    const isTooHighPrice = Number(maxPrices.maxPrice) < Number(formData.price);
    const onCheckboxChange = (event) => {
        setIsExcludedFromStatistics((previous) => !previous);
    };
    const handleCalculateButton = () => {
        saveMaximumPrice({
            data: {
                calculation_date: formData.dealDate,
                apartment_share_of_housing_company_loans: formData.apartment_share_of_housing_company_loans || 0,
                apartment_share_of_housing_company_loans_date: formData.dealDate,
                additional_info: "",
            },
            id: undefined,
            apartmentId: apartment.id,
            housingCompanyId: apartment.links.housing_company.id,
        });
        setMaxPrices({
            maxPrice: apartment.prices.maximum_prices.confirmed?.maximum_price,
            maxPricePerSquare: apartment.prices.maximum_prices.confirmed?.maximum_price
                ? apartment.prices.maximum_prices.confirmed?.maximum_price / apartment.surface_area
                : 0,
            debtFreeMaxPrice: apartment.prices.debt_free_purchase_price,
            loanAmount: apartment.prices.primary_loan_amount,
            index: data ? data.index : maxPriceQuery?.index,
        });
        setIsModalVisible(true);
    };
    console.log(apartment, maxPriceQuery, maxPriceError);
    return (
        <>
            <div className="field-sets">
                <Fieldset heading="Kaupan tiedot">
                    <div className="row">
                        <FormInputField
                            inputType="date"
                            label="Ilmoituspäivämäärä"
                            fieldPath="announcementDate"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                        <FormInputField
                            inputType="date"
                            label="Kauppakirjan päivämäärä"
                            fieldPath="dealDate"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <div className="row">
                        <div className={isTooHighPrice ? "input-field--invalid" : ""}>
                            <FormInputField
                                inputType="number"
                                label="Kauppahinta"
                                unit="€"
                                fractionDigits={2}
                                fieldPath="price"
                                formData={formData}
                                setFormData={setFormData}
                                error={error}
                            />
                            <div className="error-message error-text">
                                <span style={{display: isTooHighPrice ? "block" : "none"}}>
                                    <IconAlertCircleFill />
                                    Kauppahinta ylittää enimmäishinnan!
                                </span>
                            </div>
                        </div>
                        <FormInputField
                            inputType="number"
                            label="Osuus yhtiön lainoista"
                            unit="€"
                            fractionDigits={2}
                            fieldPath="apartment_share_of_housing_company_loans"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <Checkbox
                        id="exclude-from-stats"
                        label="Ei tilastoihin (esim. sukulaiskauppa)"
                        checked={isExcludedFromStatistics}
                        onChange={onCheckboxChange}
                    />
                    {hasValidCalculation ? (
                        <div className="max-prices">
                            <div className="row row--max-prices">
                                <div className="fieldset--max-prices__value">
                                    <legend>Enimmäishinta (€)</legend>
                                    <span className={isTooHighPrice ? "error-text" : ""}>
                                        {formatMoney(maxPrices.maxPrice as number)}
                                    </span>
                                </div>
                                <div className="fieldset--max-prices__value">
                                    <legend>Enimmäishinta per m² (€)</legend>
                                    <span>{formatMoney(maxPrices.maxPricePerSquare)}</span>
                                </div>
                                <div className="fieldset--max-prices__value">
                                    <legend>Velaton enimmäishinta (€)</legend>
                                    <span>{formatMoney(maxPrices.debtFreeMaxPrice)}</span>
                                </div>
                            </div>
                            <div className="row row--buttons">
                                <p>
                                    Enimmäishinnat <span>{formatDate(formData.dateOfCount)}</span> tehdystä
                                    enimmäishintalaskelmasta (peruste:
                                    <span> {formatIndex(data ? data.index : maxPriceQuery?.index)}</span>).
                                </p>
                                <Button
                                    theme="black"
                                    variant="secondary"
                                    onClick={handleCalculateButton}
                                >
                                    Tee uusi enimmäishintalaskelma
                                </Button>
                            </div>
                        </div>
                    ) : (
                        <div className="row row--prompt">
                            <p>
                                Asunnosta ei ole vahvistettua enimmäishintalaskelmaa, tai se ei ole enää voimassa. Syötä{" "}
                                <span>kauppakirjan päivämäärä</span> sekä <span>yhtiön lainaosuus</span>, ja tee sitten
                                uusi enimmäishintalaskelma saadaksesi asunnon enimmäishinnat kauppaa varten.
                            </p>
                            <Button
                                theme="black"
                                onClick={handleCalculateButton}
                            >
                                Tee enimmäishintalaskelma
                            </Button>
                        </div>
                    )}
                </Fieldset>
                <Fieldset heading="Omistajuudet">
                    <OwnershipsList
                        formOwnershipsList={formOwnershipsList}
                        setFormOwnershipsList={setFormOwnershipsList}
                        apartment={data}
                    />
                </Fieldset>
            </div>
            <div className="row row--buttons">
                <NavigateBackButton />
                <SaveButton
                    onClick={() => {
                        return;
                    }}
                    isLoading={false}
                />
            </div>
            <Dialog
                id="maximum-price-confirmation-modal"
                closeButtonLabelText=""
                aria-labelledby=""
                isOpen={isModalVisible}
                close={() => setIsModalVisible(false)}
                boxShadow
            >
                <Dialog.Header
                    id="maximum-price-confirmation-modal-header"
                    title="Vahvistetaanko enimmäishintalaskelma?"
                />
                <QueryStateHandler
                    data={data}
                    error={error}
                    isLoading={isLoading}
                    errorComponent={
                        <MaximumPriceModalError
                            error={error}
                            setIsModalVisible={setIsModalVisible}
                        />
                    }
                >
                    <MaximumPriceModalContent
                        calculation={data as IApartmentMaximumPrice}
                        apartment={apartment}
                        setIsModalVisible={setIsModalVisible}
                    />
                </QueryStateHandler>
            </Dialog>
        </>
    );
};

const ApartmentSalesPage = () => {
    const params = useParams();
    const {data, error, isLoading} = useGetApartmentDetailQuery({
        housingCompanyId: params.housingCompanyId as string,
        apartmentId: params.apartmentId as string,
    });

    return (
        <div className="view--apartment-sales">
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                {isLoading ? (
                    <LoadingSpinner />
                ) : (
                    <>
                        <Heading type="main">
                            Uusi kauppa
                            <span>({formatAddress(data?.address as IApartmentAddress)})</span>
                        </Heading>
                        <LoadedApartmentSalesPage apartment={data as IApartmentDetails} />
                    </>
                )}
            </QueryStateHandler>
        </div>
    );
};

export default ApartmentSalesPage;
