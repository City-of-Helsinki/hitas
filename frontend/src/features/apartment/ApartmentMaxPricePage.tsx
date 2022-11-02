import React from "react";

import {Button, Card, Fieldset, TextInput} from "hds-react";
import {useParams} from "react-router-dom";
import {useImmer} from "use-immer";

import {useGetApartmentDetailQuery} from "../../app/services";
import {FormInputField, ImprovementsTable, NavigateBackButton, QueryStateHandler} from "../../common/components";
import {IApartmentDetails} from "../../common/models";
import {formatMoney} from "../../common/utils";

const CalculationRowPrice = ({label, calculation}) => {
    return (
        <div className={`price${calculation.maximum ? " price--current-top" : ""}`}>
            <span className="basis">{label}</span>
            <span className="amount">
                <span className="value">{formatMoney(calculation.max_price)}</span>
            </span>
        </div>
    );
};

const LoadedApartmentMaxPrice = ({data}: {data: IApartmentDetails}): JSX.Element => {
    const [formData, setFormData] = useImmer({
        aaa: null,
        bbb: null,
        ccc: new Date().toISOString().split("T")[0], // Init with today's date
        ddd: null,
    });

    const calculationResponseData = {
        max_price: 223558,
        valid_until: "2022-10-05",
        index: "construction_price_index",
        calculations: {
            construction_price_index: {
                max_price: 223558,
                valid_until: "2022-10-05",
                maximum: true,
                calculation_variables: {
                    acquisition_price: 199500,
                    additional_work_during_construction: 0,
                    basic_price: 199500,
                    index_adjustment: 26401,
                    apartment_improvements: 0,
                    housing_company_improvements: 157,
                    debt_free_price: 226058,
                    debt_free_price_m2: 7535,
                    apartment_share_of_housing_company_loans: 2500,
                    completion_date: "2019-11-27",
                    completion_date_index: 129.29,
                    calculation_date: "2022-07-05",
                    calculation_date_index: 146.4,
                },
            },
            market_price_index: {
                max_price: 222343,
                valid_until: "2022-10-05",
                maximum: false,
                calculation_variables: {
                    acquisition_price: 199500,
                    additional_work_during_construction: 0,
                    basic_price: 199500,
                    index_adjustment: 25190,
                    apartment_improvements: 0,
                    housing_company_improvements: 153,
                    debt_free_price: 224843,
                    debt_free_price_m2: 7495,
                    apartment_share_of_housing_company_loans: 2500,
                    completion_date: "2019-11-27",
                    completion_date_index: 167.9,
                    calculation_date: "2022-07-05",
                    calculation_date_index: 189.1,
                },
            },
            surface_area_price_ceiling: {
                max_price: 146070,
                valid_until: "2022-08-31",
                maximum: false,
            },
        },
        apartment: {
            // TOOD
        },
        housing_company: {
            // TOOD
        },
    };

    return (
        <div className="view--create view--set-apartment">
            <h1 className="main-heading">
                {data.address.street_address} - {data.address.stair}
                {data.address.apartment_number} ({data.links.housing_company.display_name})
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
                            fieldPath="aaa"
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error="" // FIXME
                        />
                        <FormInputField
                            inputType="number"
                            unit="€"
                            label="Rakennusaikaiset parannukset"
                            fieldPath="bbb"
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error="" // FIXME
                        />
                    </div>
                    <div className="row">
                        <ImprovementsTable
                            data={data}
                            title="Laskentaan vaikuttavat yhtiön parannukset"
                        />
                    </div>
                    <div className="row">
                        <FormInputField
                            inputType="date"
                            label="Laskentapäivämäärä"
                            fieldPath="ccc"
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error="" // FIXME
                        />
                        <TextInput
                            // TODO: Localise date
                            id="calculationResponseData.valid_until"
                            label="Laskelman voimassaoloaika"
                            value={calculationResponseData.valid_until}
                            disabled
                        />
                    </div>
                    <div className="apartment-action-cards">
                        <Card>
                            <label className="card-heading">Vahvistamaton enimmäishinta</label>
                            <div className="unconfirmed-prices">
                                <CalculationRowPrice
                                    label="Markkinahintaindeksi"
                                    calculation={calculationResponseData.calculations.market_price_index}
                                />
                                <CalculationRowPrice
                                    label="Rakennushintaindeksi"
                                    calculation={calculationResponseData.calculations.construction_price_index}
                                />
                                <CalculationRowPrice
                                    label="Rajaneliöhinta"
                                    calculation={calculationResponseData.calculations.surface_area_price_ceiling}
                                />
                            </div>
                        </Card>
                    </div>
                </Fieldset>
            </div>
            <div style={{display: "flex", flexDirection: "row", justifyContent: "right", gap: "10px"}}>
                <NavigateBackButton />
                <Button theme="black">Vahvista</Button>
            </div>
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
                <LoadedApartmentMaxPrice data={data as IApartmentDetails} />
            </QueryStateHandler>
        </div>
    );
};

export default ApartmentMaxPricePage;
