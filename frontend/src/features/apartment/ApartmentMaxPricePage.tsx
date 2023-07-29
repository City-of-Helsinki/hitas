import React, {useContext, useRef} from "react";

import {Fieldset} from "hds-react";

import {zodResolver} from "@hookform/resolvers/zod";
import {FormProvider, useForm} from "react-hook-form";
import {ImprovementsTable, NavigateBackButton} from "../../common/components";
import {DateInput, FormProviderForm, NumberInput, TextAreaInput} from "../../common/components/forms";
import {ApartmentMaximumPriceWritableSchema, IApartmentMaximumPriceWritable} from "../../common/schemas";
import {today} from "../../common/utils";
import {ApartmentViewContext, ApartmentViewContextProvider} from "./components/ApartmentViewContextProvider";
import CreateMaximumPriceCalculationButton from "./components/MaximumPriceCalculationCreateButton";

const LoadedApartmentMaxPricePage = (): React.JSX.Element => {
    const {housingCompany, apartment} = useContext(ApartmentViewContext);
    if (!apartment) throw new Error("Apartment not found");

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

    const getParsedFormData = () => {
        const values = formObject.getValues();
        return {
            calculation_date: values.calculation_date as string,
            apartment_share_of_housing_company_loans_date:
                values.apartment_share_of_housing_company_loans_date as string,
            apartment_share_of_housing_company_loans: values.apartment_share_of_housing_company_loans ?? 0,
            additional_info: values.additional_info,
        };
    };

    return (
        <div className="field-sets">
            <Fieldset heading="">
                <h2 className="detail-list__heading">Laskentaan vaikuttavat asunnon tiedot</h2>
                <FormProviderForm
                    formObject={formObject}
                    formRef={formRef}
                    onSubmit={() => null}
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
                    <FormProvider {...formObject}>
                        <CreateMaximumPriceCalculationButton
                            buttonVariant="primary"
                            getParsedFormData={getParsedFormData}
                        />
                    </FormProvider>
                </div>
            </Fieldset>
        </div>
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
