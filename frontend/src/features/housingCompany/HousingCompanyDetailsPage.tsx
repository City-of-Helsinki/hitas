import React from "react";

import {StatusLabel, Tabs} from "hds-react";
import {useParams} from "react-router";

import {useGetHousingCompanyDetailQuery} from "../../app/services";
import {DetailField, QueryStateHandler} from "../../common/components";
import {IHousingCompanyDetails} from "../../common/models";
import {formatAddress} from "../../common/utils";
import {HousingCompanyApartmentResultsList} from "../apartment/ApartmentListPage";

const HousingCompanyDetailsPage = () => {
    const params = useParams();
    const {data, error, isLoading} = useGetHousingCompanyDetailQuery(params.housingCompanyId as string);

    const LoadedHousingCompanyDetails = ({data}: {data: IHousingCompanyDetails}) => {
        return (
            <>
                <h1 className="main-heading">{data.name.display}</h1>
                <div className="company-status">
                    <StatusLabel>Vapautunut 1.6.2022 ({data.state})</StatusLabel>
                </div>
                <div className="company-details">
                    <div className="tab-area">
                        <Tabs>
                            <Tabs.TabList className="tab-list">
                                <Tabs.Tab>Perustiedot</Tabs.Tab>
                                <Tabs.Tab>Lisätiedot</Tabs.Tab>
                                <Tabs.Tab>Dokumentit</Tabs.Tab>
                            </Tabs.TabList>
                            <Tabs.TabPanel>
                                <div className="company-details__tab basic-details">
                                    <div className="column">
                                        <DetailField
                                            label="Yhtiön hakunimi"
                                            value={data.name.display}
                                        />
                                        <DetailField
                                            label="Yhtiön virallinen nimi"
                                            value={data.name.official}
                                        />
                                        <DetailField
                                            label="Virallinen osoite"
                                            value={formatAddress(data.address)}
                                        />
                                        <DetailField
                                            label="Alue"
                                            value={`${data.area.name}: ${data.area.cost_area}`}
                                        />
                                        <DetailField
                                            label="Valmistumispäivä"
                                            value={data.date}
                                        />
                                        <DetailField
                                            label="Hankinta-arvo"
                                            value={`${data.acquisition_price.initial} €`} // TODO: Format number
                                        />
                                        <DetailField
                                            label="Toteutunut hankinta-arvo"
                                            value={`${data.acquisition_price.realized} €`} // TODO: Format number
                                        />
                                        <DetailField
                                            label="Ensisijaislaina"
                                            value={`${data.primary_loan} €`} // TODO: Format number
                                        />
                                        <DetailField
                                            label="Keskineliöhinta"
                                            value={`${data.summary?.average_price_per_square_meter} €/m²`}
                                        />
                                    </div>
                                    <div className="column">
                                        <DetailField
                                            label="Isännöitsijä"
                                            value={`${data.property_manager.name} (${data.property_manager.email})`}
                                        />
                                        <label className="detail-field-label">Huomioitavaa</label>
                                        <textarea
                                            readOnly
                                            value={(data.notes as string) || ""}
                                        />
                                    </div>
                                </div>
                            </Tabs.TabPanel>
                            <Tabs.TabPanel>
                                <div className="company-details__tab additional-details">
                                    <div className="column">
                                        <DetailField
                                            label="Y-tunnus"
                                            value={data.business_id}
                                        />
                                        <DetailField
                                            label="Osakkeiden lukumäärä"
                                            value={`${data.summary?.total_shares} kpl`}
                                        />
                                        <DetailField
                                            label="Huoneistojen lukumäärä"
                                            value="120"
                                        />
                                        <DetailField
                                            label="Huoneistojen pinta-ala"
                                            value={`${data.summary?.total_surface_area} m²`}
                                        />
                                        <DetailField
                                            label="Myyntihintaluettelon vahvistamispäivä"
                                            value={data.sales_price_catalogue_confirmation_date}
                                        />
                                        <DetailField
                                            label="Ilmoituspäivä"
                                            value={data.notification_date}
                                        />
                                        <DetailField
                                            label="Rakennuttaja"
                                            value={data.developer.value}
                                        />
                                    </div>
                                    <div className="column">
                                        <DetailField
                                            label="Rahoitusmuoto"
                                            value={data.financing_method.value}
                                        />
                                        <DetailField
                                            label="Talotyyppi"
                                            value={data.building_type.value}
                                        />
                                    </div>
                                </div>
                            </Tabs.TabPanel>
                            <Tabs.TabPanel>
                                <div className="company-details__tab documents">Dokumentit</div>
                            </Tabs.TabPanel>
                        </Tabs>
                    </div>
                    <div className="upgrade-list__wrapper">
                        <h2 className="upgrade-list__heading">Yhtiökohtaiset parannukset</h2>
                        <ul className="upgrade-list__list">
                            <li className="upgrade-list__list-headers">
                                <div>Nimi</div>
                                <div>Summa</div>
                                <div>Valmistumispvm</div>
                                <div>Jyvitys</div>
                            </li>
                            <li className="upgrade-list__list-item">
                                <div>Parvekelasien lisäys</div>
                                <div>340 000 €</div>
                                <div>1.1.2015</div>
                                <div>Neliöiden mukaan</div>
                            </li>
                            <li className="upgrade-list__list-item">
                                <div>Hissin rakennus</div>
                                <div>2 340 000 €</div>
                                <div>1.12.2021</div>
                                <div>Neliöiden mukaan</div>
                            </li>
                        </ul>
                    </div>
                    <div className="apartment-list__wrapper">
                        <h2>Asunnot</h2>
                        <div className="listing">
                            <HousingCompanyApartmentResultsList housingCompanyId={params.housingCompanyId} />
                        </div>
                        <div className="results"></div>
                    </div>
                </div>
            </>
        );
    };

    return (
        <div className="view--company-details">
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <LoadedHousingCompanyDetails data={data as IHousingCompanyDetails} />
            </QueryStateHandler>
        </div>
    );
};

export default HousingCompanyDetailsPage;
