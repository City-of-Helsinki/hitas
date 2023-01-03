import React, {useEffect, useState} from "react";

import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {Button, Dialog, Fieldset, IconCheck} from "hds-react";
import {useParams} from "react-router-dom";
import {useImmer} from "use-immer";

import {
    useGetApartmentDetailQuery,
    useGetHousingCompanyDetailQuery,
    useSaveApartmentMaximumPriceMutation,
} from "../../app/services";
import {
    FormInputField,
    Heading,
    ImprovementsTable,
    NavigateBackButton,
    QueryStateHandler,
} from "../../common/components";
import {
    IApartmentDetails,
    IApartmentMaximumPrice,
    IApartmentMaximumPriceWritable,
    IHousingCompanyDetails,
} from "../../common/models";
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

const LoadedApartmentMaxPrice = ({apartment}: {apartment: IApartmentDetails}): JSX.Element => {
    const [isModalVisible, setIsModalVisible] = useState<boolean>(false);
    const today = new Date().toISOString().split("T")[0]; // Today's date in YYYY-MM format
    const [formData, setFormData] = useImmer<IApartmentMaximumPriceWritable>({
        apartment_share_of_housing_company_loans: null,
        apartment_share_of_housing_company_loans_date: today,
        calculation_date: today,
        additional_info: "",
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
        <div className="view--set-apartment">
            <Heading>
                <div>
                    {apartment.address.street_address} - {apartment.address.stair}
                    {apartment.address.apartment_number} ({apartment.links.housing_company.display_name})
                </div>
            </Heading>
            <div className="field-sets">
                <Fieldset heading="">
                    <h2 className="detail-list__heading">Laskentaan vaikuttavat asunnon tiedot</h2>
                    <div className="row">
                        <div>
                            <FormInputField
                                inputType="number"
                                unit="€"
                                label="Yhtiölainaosuus"
                                fieldPath="apartment_share_of_housing_company_loans"
                                formData={formData}
                                setFormData={setFormData}
                                error={error}
                            />
                            <FormInputField
                                inputType="date"
                                label="Yhtiölainaosuuden päivämäärä"
                                fieldPath="apartment_share_of_housing_company_loans_date"
                                formData={formData}
                                setFormData={setFormData}
                                error={error}
                                maxDate={new Date(new Date().setFullYear(new Date().getFullYear() + 1))}
                                tooltipText="Jos jätetään tyhjäksi, käytetään tämänhetkistä päivää."
                            />
                            <FormInputField
                                inputType="date"
                                label="Laskentapäivämäärä"
                                fieldPath="calculation_date"
                                formData={formData}
                                setFormData={setFormData}
                                error={error}
                                maxDate={new Date()}
                                tooltipText="Jos jätetään tyhjäksi, käytetään tämänhetkistä päivää."
                            />
                        </div>
                        <FormInputField
                            inputType="textArea"
                            label="Lisätieto"
                            fieldPath="additional_info"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <ImprovementsTable
                        data={apartment}
                        title="Laskentaan vaikuttavat asunnon parannukset"
                    />
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
                    <div className="row row--buttons">
                        <NavigateBackButton />
                        <Button
                            theme="black"
                            onClick={handleCalculateButton}
                            iconLeft={<IconCheck />}
                        >
                            Laske
                        </Button>
                    </div>
                </Fieldset>
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
        <div className="view--apartment view--apartment-details">
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
