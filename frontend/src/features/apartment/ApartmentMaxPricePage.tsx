import React, {useContext, useRef, useState} from "react";

import {FetchBaseQueryError} from "@reduxjs/toolkit/query";
import {Button, Dialog, Fieldset, IconCheck} from "hds-react";

import {zodResolver} from "@hookform/resolvers/zod";
import {useForm} from "react-hook-form";
import {useSaveApartmentMaximumPriceMutation} from "../../app/services";
import {ImprovementsTable, NavigateBackButton, QueryStateHandler} from "../../common/components";
import {DateInput, FormProviderForm, NumberInput, TextAreaInput} from "../../common/components/forms";
import {
    ApartmentMaximumPriceWritableSchema,
    IApartmentMaximumPriceCalculationDetails,
    IApartmentMaximumPriceWritable,
} from "../../common/schemas";
import {hdsToast, setAPIErrorsForFormFields, today} from "../../common/utils";
import MaximumPriceModalContent from "./components/ApartmentMaximumPriceBreakdownModal";
import {ApartmentViewContext, ApartmentViewContextProvider} from "./components/ApartmentViewContextProvider";

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

const LoadedApartmentMaxPricePage = (): React.JSX.Element => {
    const {housingCompany, apartment} = useContext(ApartmentViewContext);
    if (!apartment) throw new Error("Apartment not found");

    const [isModalVisible, setIsModalVisible] = useState<boolean>(false);

    const initialFormData: IApartmentMaximumPriceWritable = {
        apartment_share_of_housing_company_loans: null,
        apartment_share_of_housing_company_loans_date: today(),
        calculation_date: today(),
        additional_info: "",
    };

    const formRef = useRef<HTMLFormElement>(null);
    const formObject = useForm({
        resolver: zodResolver(ApartmentMaximumPriceWritableSchema),
        defaultValues: initialFormData,
        mode: "all",
    });

    const [saveMaximumPrice, {data, error, isLoading}] = useSaveApartmentMaximumPriceMutation();

    const onSubmit = () => {
        // Replace apartment_share_of_housing_company_loans `null` value with a zero (API expects an integer)
        const parsedFormData = {
            ...formObject.getValues(),
            apartment_share_of_housing_company_loans:
                formObject.getValues("apartment_share_of_housing_company_loans") ?? 0,
        };

        saveMaximumPrice({
            id: undefined,
            apartmentId: apartment.id,
            housingCompanyId: apartment.links.housing_company.id,
            data: parsedFormData,
        })
            .unwrap()
            .then(() => {
                setIsModalVisible(true);
            })
            .catch((error) => {
                hdsToast.error("Asunnon enimmäishintalaskelman luominen epäonnistui!");
                setAPIErrorsForFormFields(formObject, error);
            });
    };

    return (
        <>
            <div className="field-sets">
                <Fieldset heading="">
                    <h2 className="detail-list__heading">Laskentaan vaikuttavat asunnon tiedot</h2>
                    <FormProviderForm
                        formObject={formObject}
                        formRef={formRef}
                        onSubmit={onSubmit}
                    >
                        <div className="row">
                            <div>
                                <NumberInput
                                    label="Yhtiölainaosuus"
                                    name="apartment_share_of_housing_company_loans"
                                    unit="€"
                                />
                                <DateInput
                                    label="Yhtiölainaosuuden päivämäärä"
                                    name="apartment_share_of_housing_company_loans_date"
                                    maxDate={new Date(new Date().setFullYear(new Date().getFullYear() + 1))}
                                    tooltipText="Jos jätetään tyhjäksi, käytetään tämänhetkistä päivää."
                                />
                                <DateInput
                                    label="Laskentapäivämäärä"
                                    name="calculation_date"
                                    maxDate={new Date()}
                                    tooltipText="Jos jätetään tyhjäksi, käytetään tämänhetkistä päivää."
                                />
                            </div>
                            <TextAreaInput
                                label="Lisätieto"
                                name="additional_info"
                            />
                        </div>
                    </FormProviderForm>

                    <ImprovementsTable
                        data={apartment}
                        title="Laskentaan vaikuttavat asunnon parannukset"
                    />
                    <ImprovementsTable
                        data={housingCompany}
                        title="Yhtiökohtaiset parannukset"
                    />

                    <div className="row row--buttons">
                        <NavigateBackButton />
                        <Button
                            theme="black"
                            onClick={onSubmit}
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
        </>
    );
};

const ApartmentMaxPricePage = (): React.JSX.Element => {
    return (
        <ApartmentViewContextProvider viewClassName="view--apartment-max-price">
            <LoadedApartmentMaxPricePage />
        </ApartmentViewContextProvider>
    );
};

export default ApartmentMaxPricePage;
