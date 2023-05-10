import {Button, IconPlus, StatusLabel, Tabs} from "hds-react";
import {Link, useParams} from "react-router-dom";

import {useGetHousingCompanyDetailQuery} from "../../app/services";
import {DetailField, EditButton, Heading, ImprovementsTable, QueryStateHandler} from "../../common/components";
import {getHousingCompanyHitasTypeName, getHousingCompanyRegulationStatusName} from "../../common/localisation";
import {IHousingCompanyDetails} from "../../common/schemas";
import {formatAddress, formatDate, formatMoney} from "../../common/utils";
import {HousingCompanyApartmentResultsList} from "../apartment/ApartmentListPage";

const LoadedHousingCompanyDetails = ({housingCompany}: {housingCompany: IHousingCompanyDetails}) => {
    const params = useParams() as {readonly housingCompanyId: string};
    return (
        <>
            <Heading>
                {housingCompany.name.display}
                <EditButton state={{housingCompany: housingCompany}} />
            </Heading>
            <div className="company-status">
                <StatusLabel>{getHousingCompanyHitasTypeName(housingCompany.hitas_type)}</StatusLabel>
                <StatusLabel>{housingCompany.completed ? "Valmis" : "Ei valmis"}</StatusLabel>
                {housingCompany.completed ? (
                    <>
                        <StatusLabel>
                            {housingCompany.over_thirty_years_old ? "Yli 30 vuotta" : "Alle 30 vuotta"}
                        </StatusLabel>
                        <StatusLabel>
                            {getHousingCompanyRegulationStatusName(housingCompany.regulation_status)}
                        </StatusLabel>
                    </>
                ) : null}

                {housingCompany.exclude_from_statistics ? <StatusLabel>Ei tilastoihin</StatusLabel> : null}
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
                                        value={housingCompany.name.display}
                                    />
                                    <DetailField
                                        label="Yhtiön virallinen nimi"
                                        value={housingCompany.name.official}
                                    />
                                    <DetailField
                                        label="Virallinen osoite"
                                        value={formatAddress(housingCompany.address)}
                                    />
                                    <DetailField
                                        label="Alue"
                                        value={`${housingCompany.area.name}: ${housingCompany.area.cost_area}`}
                                    />
                                    <DetailField
                                        label="Valmistumispäivä"
                                        value={formatDate(housingCompany.date)}
                                    />
                                    <DetailField
                                        label="Hankinta-arvo"
                                        value={formatMoney(housingCompany.acquisition_price)}
                                    />
                                    <DetailField
                                        label="Toteutunut hankinta-arvo"
                                        value={
                                            <>
                                                {formatMoney(housingCompany.summary.realized_acquisition_price)}
                                                {housingCompany.summary.realized_acquisition_price >
                                                    housingCompany.acquisition_price && (
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
                                        value={formatMoney(housingCompany.primary_loan)}
                                    />
                                    <DetailField
                                        label="Keskineliöhinta"
                                        value={`${housingCompany.summary?.average_price_per_square_meter} €/m²`}
                                    />
                                </div>
                                <div className="column">
                                    <DetailField
                                        label="Isännöitsijä"
                                        value={
                                            housingCompany.property_manager &&
                                            `${housingCompany.property_manager.name}
                                            ${
                                                housingCompany.property_manager.email
                                                    ? `(${housingCompany.property_manager.email})`
                                                    : ""
                                            }`
                                        }
                                    />
                                    <div>
                                        <label className="detail-field-label">Huomioitavaa</label>
                                        <textarea
                                            readOnly
                                            value={housingCompany.notes || ""}
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
                                        value={housingCompany.business_id}
                                    />
                                    <DetailField
                                        label="Osakkeiden lukumäärä"
                                        value={`${housingCompany.summary?.total_shares} kpl`}
                                    />
                                    <DetailField
                                        label="Huoneistojen lukumäärä"
                                        value="TODO"
                                    />
                                    <DetailField
                                        label="Huoneistojen pinta-ala"
                                        value={`${housingCompany.summary?.total_surface_area} m²`}
                                    />
                                    <DetailField
                                        label="Myyntihintaluettelon vahvistamispäivä"
                                        value={formatDate(housingCompany.sales_price_catalogue_confirmation_date)}
                                    />
                                    <DetailField
                                        label="Vapautumispäivä"
                                        value={formatDate(housingCompany.release_date)}
                                    />
                                    <DetailField
                                        label="Rakennuttaja"
                                        value={housingCompany.developer.value}
                                    />
                                </div>
                                <div className="column">
                                    <DetailField
                                        label="Talotyyppi"
                                        value={housingCompany.building_type.value}
                                    />
                                    <DetailField
                                        label="Yhtiön arkistotunnus"
                                        value={housingCompany.archive_id}
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
                    data={housingCompany}
                    title="Yhtiökohtaiset parannukset"
                    editableType="housingCompany"
                />
                <div style={{display: "flex", flexFlow: "row nowrap", gap: "var(--spacing-layout-s)"}}>
                    <div className="list-wrapper list-wrapper--real-estates">
                        <Heading type="list">
                            <span>Kiinteistöt</span>
                            <EditButton
                                pathname="real-estates"
                                state={{housingCompany: housingCompany}}
                            />
                        </Heading>

                        <ul className="detail-list__list">
                            {housingCompany.real_estates.map((realEstate) => (
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
                                state={{housingCompany: housingCompany}}
                            />
                        </Heading>
                        <ul className="detail-list__list">
                            {housingCompany.real_estates.flatMap((realEstate) => {
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
                <LoadedHousingCompanyDetails housingCompany={data as IHousingCompanyDetails} />
            </QueryStateHandler>
        </div>
    );
};

export default HousingCompanyDetailsPage;
