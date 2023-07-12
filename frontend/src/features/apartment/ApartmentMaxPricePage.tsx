import React, {useContext, useEffect, useState} from "react";

import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {Button, Dialog, Fieldset, IconCheck} from "hds-react";
import {useImmer} from "use-immer";

import {useGetHousingCompanyDetailQuery, useSaveApartmentMaximumPriceMutation} from "../../app/services";
import {FormInputField, ImprovementsTable, NavigateBackButton, QueryStateHandler} from "../../common/components";
import {
    IApartmentMaximumPriceCalculationDetails,
    IApartmentMaximumPriceWritable,
    IHousingCompanyDetails,
} from "../../common/schemas";
import {today} from "../../common/utils";
import MaximumPriceModalContent from "./components/ApartmentMaximumPriceBreakdownModal";
import ApartmentViewContextProvider, {ApartmentViewContext} from "./components/ApartmentViewContextProvider";

const MaximumPriceModalError = ({error, setIsModalVisible}): React.JSX.Element => {
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

const LoadedApartmentMaxPrice = (): React.JSX.Element => {
    const {apartment} = useContext(ApartmentViewContext);
    if (!apartment) throw new Error("Apartment not found");

    const [isModalVisible, setIsModalVisible] = useState<boolean>(false);
    const [formData, setFormData] = useImmer<IApartmentMaximumPriceWritable>({
        apartment_share_of_housing_company_loans: null,
        apartment_share_of_housing_company_loans_date: today(),
        calculation_date: today(),
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
        <div className="view--apartment-max-price">
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
                        calculation={data as IApartmentMaximumPriceCalculationDetails}
                        apartment={apartment}
                        setIsModalVisible={setIsModalVisible}
                    />
                </QueryStateHandler>
            </Dialog>
        </div>
    );
};

const ApartmentMaxPricePage = (): React.JSX.Element => {
    return (
        <ApartmentViewContextProvider viewClassName="view--apartment view--apartment-details">
            <LoadedApartmentMaxPrice />
        </ApartmentViewContextProvider>
    );
};

export default ApartmentMaxPricePage;
