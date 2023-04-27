import {Button, IconPlus, StatusLabel, Tabs} from "hds-react";
import {Link, useParams} from "react-router-dom";

import {useGetHousingCompanyDetailQuery} from "../../app/services";
import {DetailField, EditButton, Heading, ImprovementsTable, QueryStateHandler} from "../../common/components";
import {getHousingCompanyStateName} from "../../common/localisation";
import {IHousingCompanyDetails} from "../../common/schemas";
import {formatAddress, formatDate, formatMoney} from "../../common/utils";
import {HousingCompanyApartmentResultsList} from "../apartment/ApartmentListPage";

const LoadedHousingCompanyDetails = ({data}: {data: IHousingCompanyDetails}) => {
    const params = useParams() as {readonly housingCompanyId: string};
    return (
        <>
            <Heading>
                {data.name.display}
                <EditButton state={{housingCompany: data}} />
            </Heading>
            <div className="company-status">
                <StatusLabel>Vapautunut 1.6.2022 ({getHousingCompanyStateName(data.state)})</StatusLabel>
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
                                        value={formatDate(data.date)}
                                    />
                                    <DetailField
                                        label="Hankinta-arvo"
                                        value={formatMoney(data.acquisition_price)}
                                    />
                                    <DetailField
                                        label="Toteutunut hankinta-arvo"
                                        value={
                                            <>
                                                {formatMoney(data.summary.realized_acquisition_price)}
                                                {data.summary.realized_acquisition_price > data.acquisition_price && (
                                                    <span style={{color: "var(--color-error)"}}>
                                                        {" "}
                                                        - ylittää hankinta-arvon!
                                                    </span>
                                                )}
                                            </>
                                        }
                                    />
                                    <DetailField
                                        label="Ensisijaislaina"
                                        value={formatMoney(data.primary_loan)}
                                    />
                                    <DetailField
                                        label="Keskineliöhinta"
                                        value={`${data.summary?.average_price_per_square_meter} €/m²`}
                                    />
                                </div>
                                <div className="column">
                                    <DetailField
                                        label="Isännöitsijä"
                                        value={
                                            data.property_manager &&
                                            `${data.property_manager.name} (${data.property_manager.email})`
                                        }
                                    />
                                    <div>
                                        <label className="detail-field-label">Huomioitavaa</label>
                                        <textarea
                                            readOnly
                                            value={data.notes || ""}
                                        />
                                    </div>
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
                                        value="TODO"
                                    />
                                    <DetailField
                                        label="Huoneistojen pinta-ala"
                                        value={`${data.summary?.total_surface_area} m²`}
                                    />
                                    <DetailField
                                        label="Myyntihintaluettelon vahvistamispäivä"
                                        value={formatDate(data.sales_price_catalogue_confirmation_date)}
                                    />
                                    <DetailField
                                        label="Vapautumispäivä"
                                        value={formatDate(data.legacy_release_date)}
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
                                    <DetailField
                                        label="Yhtiön arkistotunnus"
                                        value={data.archive_id}
                                    />
                                </div>
                            </div>
                        </Tabs.TabPanel>
                        <Tabs.TabPanel>
                            <div className="company-details__tab documents">Dokumentit</div>
                        </Tabs.TabPanel>
                    </Tabs>
                </div>
                <ImprovementsTable
                    data={data}
                    title="Yhtiökohtaiset parannukset"
                    editableType="housingCompany"
                />
                <div style={{display: "flex", flexFlow: "row nowrap", gap: "var(--spacing-layout-s)"}}>
                    <div className="list-wrapper list-wrapper--real-estates">
                        <Heading type="list">
                            <span>Kiinteistöt</span>
                            <EditButton
                                pathname="real-estates"
                                state={{housingCompany: data}}
                            />
                        </Heading>

                        <ul className="detail-list__list">
                            {data.real_estates.map((realEstate) => (
                                <li
                                    className="detail-list__list-item"
                                    key={`real-estate-${realEstate.id}`}
                                >
                                    <div>{realEstate.address.street_address}</div>
                                    <div>{realEstate.property_identifier}</div>
                                </li>
                            ))}
                        </ul>
                    </div>
                    <div className="list-wrapper list-wrapper--buildings">
                        <Heading type="list">
                            <span>Rakennukset</span>
                            <EditButton
                                pathname="buildings"
                                state={{housingCompany: data}}
                            />
                        </Heading>
                        <ul className="detail-list__list">
                            {data.real_estates.flatMap((realEstate) => {
                                return realEstate.buildings.map((building) => (
                                    <li
                                        className="detail-list__list-item"
                                        key={`building-${building.id}`}
                                    >
                                        <div>{building.address.street_address}</div>
                                        <div>{building.building_identifier}</div>
                                    </li>
                                ));
                            })}
                        </ul>
                    </div>
                </div>
                <div className="list-wrapper list-wrapper--apartments">
                    <Heading type="list">
                        <span>Asunnot</span>
                        <Link to="apartments/create">
                            <Button
                                theme="black"
                                size="small"
                                iconLeft={<IconPlus />}
                            >
                                Lisää asunto
                            </Button>
                        </Link>
                    </Heading>
                    <div className="listing">
                        <HousingCompanyApartmentResultsList housingCompanyId={params.housingCompanyId} />
                    </div>
                    <div className="results" />
                </div>
            </div>
        </>
    );
};

const HousingCompanyDetailsPage = () => {
    const params = useParams() as {readonly housingCompanyId: string};
    const {data, error, isLoading} = useGetHousingCompanyDetailQuery(params.housingCompanyId);

    return (
        <div className="view--housing-company-details">
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
