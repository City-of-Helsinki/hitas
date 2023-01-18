import React, {useEffect, useState} from "react";

import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {Button, Checkbox, Dialog, Fieldset, IconAlertCircleFill} from "hds-react";
import {useNavigate, useParams} from "react-router-dom";
import {useImmer} from "use-immer";
import {v4 as uuidv4} from "uuid";

import {
    useCreateSaleMutation,
    useGetApartmentDetailQuery,
    useGetApartmentMaximumPriceQuery,
    useSaveApartmentMaximumPriceMutation,
} from "../../app/services";
import {FormInputField, Heading, NavigateBackButton, QueryStateHandler, SaveButton} from "../../common/components";
import OwnershipsList from "../../common/components/OwnershipsList";
import {IApartmentDetails, IApartmentMaximumPrice, IOwnership} from "../../common/models";
import {formatAddress, formatDate, formatIndex, formatMoney, hitasToast, today} from "../../common/utils";
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

const LoadedApartmentSalesPage = ({
    apartment,
    maxPriceCalculation,
}: {
    apartment: IApartmentDetails;
    maxPriceCalculation: IApartmentMaximumPrice | null;
}) => {
    const navigate = useNavigate();

    const [isModalVisible, setIsModalVisible] = useState(false);
    const [hasNoOwnershipsError, setHasNoOwnershipsError] = useState(false);
    const [isExcludedFromStats, setIsExcludedFromStats] = useState(false);
    const [isLoanValueChanged, setIsLoanValueChanged] = useState(false);

    const [saveSale, {data, error, isLoading}] = useCreateSaleMutation();
    const [saveMaximumPrice, {data: maxPriceData, error: maxPriceError, isLoading: isMaxPriceLoading}] =
        useSaveApartmentMaximumPriceMutation();

    const initialFormData = {
        notification_date: today(),
        purchase_date: apartment.prices.maximum_prices.confirmed?.valid.is_valid
            ? apartment.prices.maximum_prices.confirmed.calculation_date
            : "",
        purchase_price: null,
        apartment_share_of_housing_company_loans: maxPriceCalculation
            ? maxPriceCalculation.calculations.construction_price_index.calculation_variables
                  .apartment_share_of_housing_company_loans
            : null,
    };
    const [formData, setFormData] = useImmer(initialFormData);
    const [formOwnershipsList, setFormOwnershipsList] = useImmer<(IOwnership & {key: string})[]>(
        apartment !== undefined ? apartment.ownerships.map((o) => ({...o, key: uuidv4()})) : []
    );
    const [maxPrices, setMaxPrices] = useState({
        maximumPrice: apartment.prices.maximum_prices.confirmed?.maximum_price,
        maxPricePerSquare: apartment.prices.maximum_prices.confirmed?.maximum_price
            ? apartment.prices.maximum_prices.confirmed?.maximum_price / apartment.surface_area
            : 0,
        debtFreePurchasePrice: apartment.prices.debt_free_purchase_price,
        primaryLoanAmount: maxPriceCalculation
            ? maxPriceCalculation?.calculations.construction_price_index.calculation_variables
                  .apartment_share_of_housing_company_loans
            : null,
        index: maxPriceData ? maxPriceData.index : maxPriceCalculation?.index,
    });
    const isTooHighPrice = Number(maxPrices.maximumPrice) < Number(formData.purchase_price);

    const onCheckboxChange = (event) => {
        setIsExcludedFromStats(event.target.checked);
    };
    const handleCalculateButton = () => {
        saveMaximumPrice({
            data: {
                calculation_date: formData.purchase_date,
                apartment_share_of_housing_company_loans: formData.apartment_share_of_housing_company_loans || 0,
                apartment_share_of_housing_company_loans_date: formData.purchase_date,
                additional_info: "",
            },
            id: undefined,
            apartmentId: apartment.id,
            housingCompanyId: apartment.links.housing_company.id,
        }).then(() => {
            setMaxPrices({
                maximumPrice: apartment.prices.maximum_prices.confirmed?.maximum_price,
                maxPricePerSquare: apartment.prices.maximum_prices.confirmed?.maximum_price
                    ? apartment.prices.maximum_prices.confirmed?.maximum_price / apartment.surface_area
                    : 0,
                debtFreePurchasePrice: apartment.prices.debt_free_purchase_price,
                primaryLoanAmount: apartment.prices.primary_loan_amount,
                index: maxPriceData ? maxPriceData.index : maxPriceCalculation?.index,
            });
            setIsModalVisible(true);
        });
    };
    const handleSaveButton = () => {
        if (formOwnershipsList.length < 1) {
            hitasToast("Kaupalla täytyy olla ainakin yksi omistaja!", "error");
            setHasNoOwnershipsError(true);
        } else {
            const saleData = {
                ...formData,
                ownerships: formOwnershipsList,
                exclude_from_statistics: isExcludedFromStats,
            };
            saveSale({
                data: saleData,
                apartmentId: apartment.id,
                housingCompanyId: apartment.links.housing_company.id,
            });
        }
    };

    // Handle saving flow
    useEffect(() => {
        if (!isLoading && !error && data && data.id) {
            hitasToast("Kauppa tallennettu onnistuneesti!");
            navigate(`/housing-companies/${apartment.links.housing_company.id}/apartments/${apartment.id}`);
        } else if (error) {
            hitasToast("Kaupan tallentaminen epäonnistui.", "error");
        }
    }, [isLoading, error, data, navigate, apartment.links.housing_company.id, apartment.id]);
    // Handle alert for changed loan value
    useEffect(() => {
        if (
            Number(formData.apartment_share_of_housing_company_loans) !==
                maxPriceCalculation?.calculations[maxPriceCalculation.index].calculation_variables
                    .apartment_share_of_housing_company_loans &&
            maxPriceCalculation
        )
            setIsLoanValueChanged(true);
        else setIsLoanValueChanged(false);
    }, [
        formData.apartment_share_of_housing_company_loans,
        maxPriceCalculation,
        setIsLoanValueChanged,
        isLoanValueChanged,
    ]);
    console.log(maxPriceCalculation);
    console.log(formData);
    return (
        <>
            <div className="field-sets">
                <Fieldset heading="Kaupan tiedot">
                    <div className="row">
                        <FormInputField
                            inputType="date"
                            label="Ilmoituspäivämäärä"
                            fieldPath="notification_date"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                            required
                        />
                        <FormInputField
                            inputType="date"
                            label="Kauppakirjan päivämäärä"
                            fieldPath="purchase_date"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                            required
                        />
                    </div>
                    <div className="row">
                        <div className={isTooHighPrice ? "input-field--invalid" : ""}>
                            <FormInputField
                                inputType="number"
                                label="Kauppahinta"
                                unit="€"
                                fractionDigits={2}
                                fieldPath="purchase_price"
                                formData={formData}
                                setFormData={setFormData}
                                error={error}
                                required
                            />
                            <div className="error-message error-text">
                                <span style={{display: isTooHighPrice ? "block" : "none"}}>
                                    <IconAlertCircleFill />
                                    Kauppahinta ylittää enimmäishinnan!
                                </span>
                            </div>
                        </div>
                        <div>
                            <FormInputField
                                inputType="number"
                                label="Osuus yhtiön lainoista"
                                unit="€"
                                fractionDigits={2}
                                fieldPath="apartment_share_of_housing_company_loans"
                                formData={formData}
                                setFormData={setFormData}
                                error={error}
                                required
                            />
                            <div className="error-message error-text">
                                <span style={{display: isLoanValueChanged ? "block" : "none"}}>
                                    Lainaosuus muuttui, tee uusi laskelma!
                                </span>
                            </div>
                        </div>
                    </div>
                    <Checkbox
                        id="exclude-from-stats"
                        label="Ei tilastoihin (esim. sukulaiskauppa)"
                        checked={isExcludedFromStats}
                        onChange={(event) => onCheckboxChange(event)}
                    />
                    {maxPriceCalculation ? (
                        <div className="max-prices">
                            <div className="row row--max-prices">
                                <div className="fieldset--max-prices__value">
                                    <legend>Enimmäishinta (€)</legend>
                                    <span className={isTooHighPrice ? "error-text" : ""}>
                                        {formatMoney(maxPrices.maximumPrice as number)}
                                    </span>
                                </div>
                                <div className="fieldset--max-prices__value">
                                    <legend>Enimmäishinta per m² (€)</legend>
                                    <span>{formatMoney(maxPrices.maxPricePerSquare)}</span>
                                </div>
                                <div className="fieldset--max-prices__value">
                                    <legend>Velaton enimmäishinta (€)</legend>
                                    <span>{formatMoney(maxPrices.debtFreePurchasePrice)}</span>
                                </div>
                            </div>
                            <div className="row row--buttons">
                                <p>
                                    Enimmäishinnat{" "}
                                    <span>
                                        {formatDate(apartment.prices.maximum_prices.confirmed?.confirmed_at as string)}
                                    </span>{" "}
                                    vahvistetusta enimmäishintalaskelmasta (peruste:
                                    <span>
                                        {" "}
                                        {formatIndex(maxPriceData ? maxPriceData.index : maxPriceCalculation.index)}
                                    </span>
                                    ).
                                    {isLoanValueChanged && (
                                        <span>
                                            <br />
                                            Lainaosuus eri kuin laskelmassa!
                                        </span>
                                    )}
                                </p>
                                <Button
                                    theme="black"
                                    variant={isLoanValueChanged ? "primary" : "secondary"}
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
                <Fieldset
                    className="ownerships-fieldset"
                    heading="Omistajuudet *"
                >
                    <OwnershipsList
                        formOwnershipsList={formOwnershipsList}
                        setFormOwnershipsList={setFormOwnershipsList}
                        noOwnersError={hasNoOwnershipsError}
                    />
                </Fieldset>
            </div>
            <div className="row row--buttons">
                <NavigateBackButton />
                <SaveButton
                    onClick={handleSaveButton}
                    isLoading={isLoading}
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
                    data={maxPriceData}
                    error={maxPriceError}
                    isLoading={isMaxPriceLoading}
                    errorComponent={
                        <MaximumPriceModalError
                            error={maxPriceError}
                            setIsModalVisible={setIsModalVisible}
                        />
                    }
                >
                    <MaximumPriceModalContent
                        calculation={maxPriceData as IApartmentMaximumPrice}
                        apartment={apartment}
                        setIsModalVisible={setIsModalVisible}
                    />
                </QueryStateHandler>
            </Dialog>
        </>
    );
};

const MaxPriceCalculationLoader = ({apartment}) => {
    const hasValidCalculation = apartment.prices.maximum_prices.confirmed?.valid.is_valid;

    const {data, error, isLoading} = useGetApartmentMaximumPriceQuery({
        housingCompanyId: apartment.links.housing_company.id,
        apartmentId: apartment.id,
        priceId: apartment.prices.maximum_prices.confirmed?.id as string,
    });

    if (hasValidCalculation) {
        return (
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <Heading type="main">
                    Uusi kauppa
                    <span>({formatAddress(apartment.address)})</span>
                </Heading>
                <LoadedApartmentSalesPage
                    maxPriceCalculation={data as IApartmentMaximumPrice}
                    apartment={apartment}
                />
            </QueryStateHandler>
        );
    } else
        return (
            <>
                <Heading type="main">
                    Uusi kauppa
                    <span>({formatAddress(apartment.address)})</span>
                </Heading>
                <LoadedApartmentSalesPage
                    maxPriceCalculation={null}
                    apartment={apartment}
                />
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
                <MaxPriceCalculationLoader apartment={data as IApartmentDetails} />
            </QueryStateHandler>
        </div>
    );
};

export default ApartmentSalesPage;
