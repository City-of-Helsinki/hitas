import React, {useEffect, useState} from "react";

import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {Button, Dialog, Fieldset, IconCheck} from "hds-react";
import {useNavigate, useParams} from "react-router-dom";
import {useImmer} from "use-immer";

import {
    useGetApartmentDetailQuery,
    useGetHousingCompanyDetailQuery,
    useSaveApartmentMaximumPriceMutation,
} from "../../app/services";
import {
    FormInputField,
    ImprovementsTable,
    NavigateBackButton,
    QueryStateHandler,
    SaveButton,
} from "../../common/components";
import {
    IApartmentDetails,
    IApartmentMaximumPrice,
    IApartmentMaximumPriceWritable,
    IHousingCompanyDetails,
} from "../../common/models";
import {formatMoney, hitasToast} from "../../common/utils";

const CalculationRowPrice = ({label, calculation}) => {
    const maximumBoldedStyle = calculation.maximum ? {fontWeight: 700} : {};
    return (
        <div>
            <p style={maximumBoldedStyle}>{label}</p>
            <p style={maximumBoldedStyle}>{formatMoney(calculation.max_price)}</p>
        </div>
    );
};

const MaximumPriceModalContent = ({
    calculation,
    apartment,
    setIsModalVisible,
}: {
    calculation: IApartmentMaximumPrice;
    apartment: IApartmentDetails;
    setIsModalVisible;
}) => {
    const navigate = useNavigate();
    const [confirmMaximumPrice, {data, error, isLoading}] = useSaveApartmentMaximumPriceMutation();

    const handleConfirmButton = () => {
        confirmMaximumPrice({
            data: {confirm: true},
            id: calculation.id,
            apartmentId: apartment.id,
            housingCompanyId: apartment.links.housing_company.id,
        });
        setIsModalVisible(true);
    };

    useEffect(() => {
        if (!isLoading && !error && data && data.confirmed_at) {
            hitasToast("Enimmäishinta vahvistettu!");
            navigate(`/housing-companies/${apartment.links.housing_company.id}/apartments/${apartment.id}`);
        }
    }, [apartment, data, error, isLoading, navigate]);

    return (
        <>
            <Dialog.Content>
                <div>
                    <CalculationRowPrice
                        label="Markkinahintaindeksi"
                        calculation={calculation.calculations.market_price_index}
                    />
                    <CalculationRowPrice
                        label="Rakennushintaindeksi"
                        calculation={calculation.calculations.construction_price_index}
                    />
                    <CalculationRowPrice
                        label="Rajaneliöhinta"
                        calculation={calculation.calculations.surface_area_price_ceiling}
                    />
                    <div>
                        <p>Laskelman voimassaoloaika</p>
                        <p>{calculation.valid_until}</p>
                    </div>
                </div>
            </Dialog.Content>
            <Dialog.ActionButtons className="align-content-right">
                <Button
                    onClick={() => setIsModalVisible(false)}
                    variant="secondary"
                    theme="black"
                >
                    Peruuta
                </Button>
                <SaveButton
                    onClick={() => handleConfirmButton()}
                    isLoading={isLoading}
                />
            </Dialog.ActionButtons>
        </>
    );
};

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

const LoadedApartmentMaxPrice = ({apartment}: {apartment: IApartmentDetails}): JSX.Element => {
    const [isModalVisible, setIsModalVisible] = useState<boolean>(false);
    const [formData, setFormData] = useImmer<IApartmentMaximumPriceWritable>({
        calculation_date: new Date().toISOString().split("T")[0], // Init with today's date in YYYY-MM format
        apartment_share_of_housing_company_loans: null,
    });
    const {
        data: housingCompanyData,
        error: housingCompanyError,
        isLoading: isHousingCompanyLoading,
    } = useGetHousingCompanyDetailQuery(apartment.links.housing_company.id);
    const [saveMaximumPrice, {data, error, isLoading}] = useSaveApartmentMaximumPriceMutation();

    useEffect(() => {
        // Field errors, don't show modal as they are displayed on the fields instead
        if ((error as {data?: {fields: []}})?.data?.fields?.length) {
            setIsModalVisible(false);
        }
    }, [error]);

    const handleCalculateButton = () => {
        // Replace apartment_share_of_housing_company_loans `null` value with a zero (API expects an integer)
        const parsedFormData = {
            ...formData,
            apartment_share_of_housing_company_loans: formData.apartment_share_of_housing_company_loans || 0,
        };

        saveMaximumPrice({
            data: parsedFormData,
            id: undefined,
            apartmentId: apartment.id,
            housingCompanyId: apartment.links.housing_company.id,
        });

        setIsModalVisible(true);
    };

    return (
        <div className="view--create view--set-apartment">
            <h1 className="main-heading">
                {apartment.address.street_address} - {apartment.address.stair}
                {apartment.address.apartment_number} ({apartment.links.housing_company.display_name})
            </h1>
            <div className="field-sets">
                <Fieldset heading="">
                    <div className="row">
                        <h2 className="detail-list__heading">Laskentaan vaikuttavat asunnon tiedot</h2>
                    </div>
                    <div className="row">
                        <FormInputField
                            inputType="number"
                            unit="€"
                            label="Yhtiölainaosuus"
                            fieldPath="apartment_share_of_housing_company_loans"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <div className="row">
                        <ImprovementsTable
                            data={apartment}
                            title="Laskentaan vaikuttavat yhtiön parannukset"
                        />
                    </div>
                    <div className="row">
                        <QueryStateHandler
                            data={housingCompanyData}
                            error={housingCompanyError}
                            isLoading={isHousingCompanyLoading}
                        >
                            <ImprovementsTable
                                data={housingCompanyData as IHousingCompanyDetails}
                                title="Yhtiökohtaiset parannukset"
                            />
                        </QueryStateHandler>
                    </div>
                    <div className="row">
                        <FormInputField
                            inputType="date"
                            label="Laskentapäivämäärä"
                            fieldPath="calculation_date"
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                </Fieldset>
            </div>
            <div
                className="align-content-right"
                style={{marginTop: "10px"}}
            >
                <NavigateBackButton />
                <Button
                    theme="black"
                    onClick={handleCalculateButton}
                    iconLeft={<IconCheck />}
                >
                    Laske
                </Button>
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
                    title="Vahvistetaanko enimmäishinnan laskelma?"
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
        </div>
    );
};

const ApartmentMaxPricePage = (): JSX.Element => {
    const params = useParams();
    const {data, error, isLoading} = useGetApartmentDetailQuery({
        housingCompanyId: params.housingCompanyId as string,
        apartmentId: params.apartmentId as string,
    });

    return (
        <div className="view--apartment-details">
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <LoadedApartmentMaxPrice apartment={data as IApartmentDetails} />
            </QueryStateHandler>
        </div>
    );
};

export default ApartmentMaxPricePage;
