import React, {useEffect, useRef, useState} from "react";

import {zodResolver} from "@hookform/resolvers/zod";
import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {Button, Dialog, Fieldset, IconAlertCircleFill} from "hds-react";
import {useForm} from "react-hook-form";
import {useNavigate, useParams} from "react-router-dom";
import {v4 as uuidv4} from "uuid";

import {
    useCreateSaleMutation,
    useGetApartmentDetailQuery,
    useGetApartmentMaximumPriceQuery,
    useSaveApartmentMaximumPriceMutation,
} from "../../app/services";
import {Heading, NavigateBackButton, QueryStateHandler, SaveButton} from "../../common/components";
import OwnershipsList from "../../common/components/OwnershipsList";
import {Checkbox, DateInput, NumberInput} from "../../common/components/form";
import {ApartmentSaleSchema, IApartmentDetails, IApartmentMaximumPrice, IApartmentSaleForm} from "../../common/schemas";
import {formatDate, formatIndex, formatMoney, hdsToast, today} from "../../common/utils";
import ApartmentHeader from "./components/ApartmentHeader";
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
    // We need a reference to the formik form-element, to be able to dispatch a submit event dynamically
    const formRef = useRef<HTMLFormElement | null>(null);
    // Queries and mutations
    const [saveSale, {data, error, isLoading}] = useCreateSaleMutation();
    const [saveMaximumPrice, {data: maxPriceData, error: maxPriceError, isLoading: isMaxPriceLoading}] =
        useSaveApartmentMaximumPriceMutation();

    // Form data, schema and variables
    const initialFormData: IApartmentSaleForm = {
        notification_date: today(),
        purchase_date: apartment.prices.maximum_prices.confirmed?.valid.is_valid
            ? apartment.prices.maximum_prices.confirmed.calculation_date
            : "",
        purchase_price: null,
        apartment_share_of_housing_company_loans: maxPriceCalculation
            ? maxPriceCalculation.calculations.construction_price_index.calculation_variables
                  .apartment_share_of_housing_company_loans
            : null,
        exclude_from_statistics: false,
    };
    const formOwnershipsList = apartment.ownerships.map((o) => ({...o, key: uuidv4()}));
    const formObject = useForm({
        defaultValues: {...initialFormData, ownerships: formOwnershipsList},
        mode: "all",
        resolver: zodResolver(ApartmentSaleSchema),
    });
    const {
        formState: {isDirty, isValid, errors},
    } = formObject;

    //  Maximum price calculation variables
    const [maxPrices, setMaxPrices] = useState({
        maximumPrice: apartment.prices.maximum_prices.confirmed?.maximum_price,
        maxPricePerSquare: maxPriceCalculation
            ? maxPriceCalculation.calculations.construction_price_index.calculation_variables.debt_free_price_m2
            : maxPriceData?.calculations.construction_price_index.calculation_variables.debt_free_price_m2,
        debtFreePurchasePrice: maxPriceCalculation
            ? maxPriceCalculation.calculations.construction_price_index.calculation_variables.debt_free_price
            : maxPriceData?.calculations.construction_price_index.calculation_variables.debt_free_price,
        index: maxPriceData ? maxPriceData.index : maxPriceCalculation?.index,
    });

    // Flags
    const [isModalVisible, setIsModalVisible] = useState(false);
    const isTooHighPrice = Number(maxPrices.maximumPrice) < Number(formObject.getValues("purchase_price"));
    const isLoanValueChanged =
        Number(formObject.getValues("apartment_share_of_housing_company_loans")) !==
            maxPriceCalculation?.calculations[maxPriceCalculation.index].calculation_variables
                .apartment_share_of_housing_company_loans && maxPriceCalculation;
    const hasNoOwnershipsError = !!formOwnershipsList.length;

    // Handle "calculate maximum price"-button press
    const handleCalculateButton = () => {
        if (formObject.getValues("purchase_date") && formObject.getValues("apartment_share_of_housing_company_loans")) {
            // Validate relevant fields for the calculation
            if (errors.purchase_date || errors.apartment_share_of_housing_company_loans) {
                if (errors.purchase_date)
                    hdsToast.error(
                        <>
                            Tarkista <span>kauppakirjan päivämäärä</span>!
                        </>
                    );
                else
                    hdsToast.error(
                        <>
                            Tarkista <span>yhtiön lainaosuus</span>!
                        </>
                    );
            } else handleValidatedCalculation();
        } else
            hdsToast.error(
                <>
                    Enimmäishintojen laskemiseen tarvitaan <span>kauppakirjan päivämäärä</span> sekä{" "}
                    <span>yhtiön lainaosuus</span>!
                </>
            );
    };

    const handleValidatedCalculation = () => {
        if (formObject.getValues("purchase_date") && formObject.getValues("apartment_share_of_housing_company_loans")) {
            saveMaximumPrice({
                data: {
                    calculation_date: formObject.getValues("purchase_date"),
                    apartment_share_of_housing_company_loans:
                        formObject.getValues("apartment_share_of_housing_company_loans") || 0,
                    apartment_share_of_housing_company_loans_date: formObject.getValues("purchase_date"),
                    additional_info: "",
                },
                id: undefined,
                apartmentId: apartment.id,
                housingCompanyId: apartment.links.housing_company.id,
            }).then(() => {
                setMaxPrices({
                    maximumPrice: apartment.prices.maximum_prices.confirmed?.maximum_price,
                    maxPricePerSquare: maxPriceCalculation
                        ? maxPriceCalculation.calculations.construction_price_index.calculation_variables
                              .debt_free_price_m2
                        : maxPriceData?.calculations.construction_price_index.calculation_variables.debt_free_price_m2,
                    debtFreePurchasePrice: maxPriceCalculation
                        ? maxPriceCalculation.calculations.construction_price_index.calculation_variables
                              .debt_free_price
                        : maxPriceData?.calculations.construction_price_index.calculation_variables.debt_free_price,
                    index: maxPriceData ? maxPriceData.index : maxPriceCalculation?.index,
                });
                setIsModalVisible(true);
            });
        }
    };

    // Dispatch submit event, as the "Tallenna"-button isn't inside the sale form element
    const handleSaveButton = () => {
        formRef.current && formRef.current.dispatchEvent(new Event("submit", {cancelable: true, bubbles: true}));
    };

    // Handle form submit event
    const onSubmit = (data) => {
        saveSale({
            data: data,
            apartmentId: apartment.id,
            housingCompanyId: apartment.links.housing_company.id,
        });
    };

    // Handle saving flow and navigate the user back to the apartment's details view upon success
    useEffect(() => {
        if (!isLoading && !error && data && data.id) {
            hdsToast.success("Kauppa tallennettu onnistuneesti!");
            navigate(`/housing-companies/${apartment.links.housing_company.id}/apartments/${apartment.id}`);
        } else if (error) {
            hdsToast.error("Kaupan tallentaminen epäonnistui.");
        }
    }, [isLoading, error, data, navigate, apartment.links.housing_company.id, apartment.id]);

    const MaximumPriceCalculationExists = ({maxPriceCalculation}) => {
        return (
            <div className="max-prices">
                <div className="row row--max-prices">
                    <div className={`fieldset--max-prices__value ${isLoanValueChanged ? " expired" : ""}`}>
                        <legend>Enimmäishinta (€)</legend>
                        <span className={isTooHighPrice ? "error-text" : ""}>
                            {formatMoney(maxPrices.maximumPrice as number)}
                        </span>
                    </div>
                    <div className={`fieldset--max-prices__value ${isLoanValueChanged ? " expired" : ""}`}>
                        <legend>Enimmäishinta per m² (€)</legend>
                        <span>{formatMoney(maxPrices.maxPricePerSquare)}</span>
                    </div>
                    <div className={`fieldset--max-prices__value ${isLoanValueChanged ? " expired" : ""}`}>
                        <legend>Velaton enimmäishinta (€)</legend>
                        <span>{formatMoney(maxPrices.debtFreePurchasePrice)}</span>
                    </div>
                </div>
                <div className="row row--prompt">
                    <p>
                        Enimmäishinnat ovat laskettu{" "}
                        <span>
                            {` ${formatIndex(maxPriceData ? maxPriceData.index : maxPriceCalculation.index)}llä`}
                        </span>{" "}
                        ja{" "}
                        <span>
                            {formatMoney(
                                maxPriceCalculation?.calculations[maxPriceCalculation.index].calculation_variables
                                    .apartment_share_of_housing_company_loans
                            )}
                        </span>{" "}
                        lainaosuudella.{" "}
                    </p>
                    {isLoanValueChanged && (
                        <p className="error-text">
                            <span>Yhtiön lainaosuus</span> on muuttunut, ole hyvä ja
                            <span> tee uusi enimmäishintalaskelma</span>.
                        </p>
                    )}
                    <Button
                        theme="black"
                        variant={isLoanValueChanged ? "primary" : "secondary"}
                        onClick={handleCalculateButton}
                        disabled={
                            !formObject.getValues("purchase_date") ||
                            !formObject.getValues("apartment_share_of_housing_company_loans")
                        }
                    >
                        Tee uusi enimmäishintalaskelma
                    </Button>
                </div>
            </div>
        );
    };
    const MaximumPriceCalculationMissing = () => {
        return (
            <div className="row row--prompt">
                <p>
                    Asunnosta ei ole vahvistettua enimmäishintalaskelmaa, tai se ei ole enää voimassa. Syötä{" "}
                    <span>kauppakirjan päivämäärä</span> sekä <span>yhtiön lainaosuus</span>, ja tee sitten uusi
                    enimmäishintalaskelma saadaksesi asunnon enimmäishinnat kauppaa varten.
                </p>
                <Button
                    theme="black"
                    onClick={handleCalculateButton}
                    disabled={
                        !formObject.getValues("purchase_date") ||
                        !formObject.getValues("apartment_share_of_housing_company_loans")
                    }
                >
                    Tee enimmäishintalaskelma
                </Button>
            </div>
        );
    };
    return (
        <>
            <div className="field-sets">
                <Fieldset heading="Kaupan tiedot">
                    <form
                        ref={formRef}
                        onSubmit={formObject.handleSubmit(onSubmit, (errors) => console.warn(errors))}
                    >
                        <div className="row">
                            <DateInput
                                name="notification_date"
                                label="Ilmoituspäivämäärä"
                                formObject={formObject}
                                maxDate={new Date()}
                                required
                            />
                            <DateInput
                                name="purchase_date"
                                label="Kauppakirjan päivämäärä"
                                formObject={formObject}
                                maxDate={new Date()}
                                required
                            />
                        </div>
                        <div className="row">
                            <div className={isTooHighPrice ? "input-field--invalid" : ""}>
                                <NumberInput
                                    name="purchase_price"
                                    label="Kauppahinta"
                                    formObject={formObject}
                                    unit="€"
                                    fractionDigits={2}
                                    required
                                />
                                <div className="error-message error-text">
                                    <span style={{display: isTooHighPrice ? "block" : "none"}}>
                                        <IconAlertCircleFill />
                                        Kauppahinta ylittää enimmäishinnan!
                                    </span>
                                </div>
                            </div>
                            <div className={isLoanValueChanged ? "input-field--invalid" : ""}>
                                <NumberInput
                                    name="apartment_share_of_housing_company_loans"
                                    label="Osuus yhtiön lainoista"
                                    formObject={formObject}
                                    unit="€"
                                    required
                                />
                                <div className="error-message error-text">
                                    <span style={{display: isLoanValueChanged ? "block" : "none"}}>
                                        <IconAlertCircleFill />
                                        Eri kuin enimmäishintalaskelmassa!
                                    </span>
                                </div>
                            </div>
                        </div>
                        <Checkbox
                            name="exclude_from_statistics"
                            label="Ei tilastoihin (esim. sukulaiskauppa)"
                            formObject={formObject}
                        />
                    </form>
                </Fieldset>
                <Fieldset
                    heading={`Enimmäishintalaskelma ${
                        maxPriceCalculation
                            ? `(vahvistettu ${formatDate(
                                  apartment.prices.maximum_prices.confirmed?.confirmed_at as string
                              )})`
                            : ""
                    } *`}
                >
                    {maxPriceCalculation ? (
                        <MaximumPriceCalculationExists maxPriceCalculation={maxPriceCalculation} />
                    ) : (
                        <MaximumPriceCalculationMissing />
                    )}
                </Fieldset>
                <Fieldset
                    className="ownerships-fieldset"
                    heading="Omistajuudet *"
                >
                    <OwnershipsList
                        formOwnershipsList={formOwnershipsList}
                        noOwnersError={hasNoOwnershipsError}
                        formObject={formObject}
                    />
                </Fieldset>
            </div>
            <div className="row row--buttons">
                <NavigateBackButton />
                <SaveButton
                    onClick={handleSaveButton}
                    isLoading={isLoading}
                    disabled={!isDirty || !isValid}
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

    const SalesHeading = () => (
        <>
            <ApartmentHeader apartment={apartment} />
            <Heading type="main">Kauppatapahtuma</Heading>
        </>
    );

    if (hasValidCalculation) {
        return (
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <SalesHeading />
                <LoadedApartmentSalesPage
                    maxPriceCalculation={data as IApartmentMaximumPrice}
                    apartment={apartment}
                />
            </QueryStateHandler>
        );
    } else
        return (
            <>
                <SalesHeading />
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
