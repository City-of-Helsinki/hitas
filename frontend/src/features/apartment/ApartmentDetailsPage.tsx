import React from "react";

import {Button, Card, IconLock, IconLockOpen, StatusLabel, Tabs} from "hds-react";
import {Link, useParams} from "react-router-dom";

import {useGetApartmentDetailQuery, useGetHousingCompanyDetailQuery} from "../../app/services";
import {DetailField, EditButton, ImprovementsTable, QueryStateHandler} from "../../common/components";
import {IApartmentDetails, IHousingCompanyDetails, IOwnership} from "../../common/models";
import {formatAddress, formatDate, formatMoney} from "../../common/utils";

const SalesCondition = ({
    name,
    address,
    url,
    isConfirmed,
}: {
    name: string;
    address: string;
    url?: string;
    isConfirmed: boolean;
}): JSX.Element => (
    <div className={"sales-condition"}>
        <div className="icon-container">
            {isConfirmed ? (
                <IconLock
                    size="m"
                    aria-hidden="true"
                />
            ) : (
                <IconLockOpen
                    size="m"
                    aria-hidden="true"
                />
            )}
        </div>
        <div>
            <p>{name}</p>
            <p>{address}</p>
            <p className="link">
                {url === undefined || null ? (
                    <span>Katso asunto vanhasta rekisteristä!</span>
                ) : (
                    <Link to={url}>Katso myytävä asunto</Link>
                )}
            </p>
        </div>
    </div>
);

const LoadedApartmentDetails = ({data}: {data}): JSX.Element => {
    const params = useParams();
    const {
        data: housingCompanyData,
        error: housingCompanyError,
        isLoading: housingCompanyIsLoading,
    } = useGetHousingCompanyDetailQuery(params.housingCompanyId as string);
    const isPre2011 = data.prices.max_prices.unconfirmed.pre_2011 !== null;
    const unconfirmedPrices = isPre2011
        ? data.prices.max_prices.unconfirmed.pre_2011
        : data.prices.max_prices.unconfirmed.onwards_2011;
    return (
        <>
            <h1 className={"main-heading"}>
                <Link to={`/housing-companies/${data.links.housing_company.id}`}>
                    <span className={"name"}>{data.links.housing_company.display_name}</span>
                    <span className="address">{formatAddress(data.address)}</span>
                    <StatusLabel>{data.state}</StatusLabel>
                </Link>
                <EditButton state={{apartment: data}} />
            </h1>
            <h2 className={"apartment-stats"}>
                <span className="apartment-stats--number">
                    {data.address.stair}
                    {data.address.apartment_number}
                </span>
                <span>
                    {data.rooms}
                    {data.type.value}
                </span>
                <span>{data.surface_area}m²</span>
                <span>{data.address.floor}.krs</span>
            </h2>
            <div className="apartment-action-cards">
                <Card>
                    <label className="card-heading">Vahvistamaton enimmäishinta</label>
                    <div className="unconfirmed-prices">
                        <div
                            className={`price${
                                unconfirmedPrices.market_price_index.maximum ? " price--current-top" : ""
                            }`}
                        >
                            <span className="basis">Markkinahintaindeksi</span>
                            <span className="amount">
                                <span className="value">{formatMoney(unconfirmedPrices.market_price_index.value)}</span>
                            </span>
                        </div>
                        <div
                            className={`price${
                                unconfirmedPrices.construction_price_index.maximum ? " price--current-top" : ""
                            }`}
                        >
                            <span className="basis">Rakennushintaindeksi</span>
                            <span className="amount">
                                <span className="value">
                                    {formatMoney(unconfirmedPrices.construction_price_index.value)}
                                </span>
                            </span>
                        </div>
                        <div
                            className={`price${
                                unconfirmedPrices.surface_area_price_ceiling.maximum ? " price--current-top" : ""
                            }`}
                        >
                            <span className="basis">Rajaneliöhinta</span>
                            <span className="amount">
                                <span className="value">
                                    {formatMoney(unconfirmedPrices.surface_area_price_ceiling.value)}
                                </span>
                            </span>
                        </div>
                    </div>
                    <label className="card-heading">Vahvistettu enimmäishinta</label>
                    <p className="confirmed-price">TODO</p>
                    <Button
                        className="button-confirm"
                        theme="black"
                        size="small"
                        style={{display: "none"}} // Hidden until it's
                    >
                        Vahvista
                    </Button>
                </Card>
                <Card>
                    <label className="card-heading">Vahvistettu myyntiehto</label>
                    <SalesCondition
                        name="Arabian unelma (valm.2015)"
                        address="Arabiankatu 5 C 2, 00440"
                        url={`/housing-companies/${data.links.housing_company.id}`}
                        isConfirmed={true}
                    />
                    <label className="card-heading">Vahvistamaton myyntiehto</label>
                    <SalesCondition
                        name="Keimolan Ylpeys (valm.2015)"
                        address="Kierretie 5 D 5"
                        isConfirmed={false}
                    />
                </Card>
            </div>
            <div className="apartment-details">
                <div className="tab-area">
                    <Tabs>
                        <Tabs.TabList className="tab-list">
                            <Tabs.Tab>Perustiedot</Tabs.Tab>
                            <Tabs.Tab>Dokumentit</Tabs.Tab>
                        </Tabs.TabList>
                        <Tabs.TabPanel>
                            <div className="company-details__tab basic-details">
                                <div className="row">
                                    <DetailField
                                        label="Kauppakirjahinta"
                                        value={formatMoney(data.prices.purchase_price)}
                                    />
                                    <DetailField
                                        label="Hankinta-arvo"
                                        value={formatMoney(data.prices.acquisition_price)}
                                    />
                                    <DetailField
                                        label="Valmistumispäivä"
                                        value={formatDate(data.completion_date)}
                                    />
                                </div>
                                <div className="columns">
                                    <div className="column">
                                        <label className="detail-field-label">Omistajat</label>
                                        {data.ownerships.map((ownership: IOwnership) => (
                                            <DetailField
                                                key={ownership.owner.id}
                                                value={
                                                    <>
                                                        {`${ownership.owner.name} (${ownership.owner.identifier})`}
                                                        <span> {ownership.percentage}%</span>
                                                    </>
                                                }
                                                label={""}
                                            />
                                        ))}
                                        <DetailField
                                            label="Isännöitsijä"
                                            value="TODO"
                                        />
                                        <label className="detail-field-label">Huomioitavaa</label>
                                        <textarea
                                            value={(data.notes as string) || ""}
                                            readOnly
                                        />
                                    </div>
                                    <div className="column">
                                        <DetailField
                                            label="Osakkeiden lukumäärä"
                                            value={data.shares ? data.shares.total : 0}
                                        />
                                        {data.shares && (
                                            <DetailField
                                                label="Osakkeet"
                                                value={`${data.shares.start} - ${data.shares.end}`}
                                            />
                                        )}
                                        <DetailField
                                            label="Luovutushinta"
                                            value={formatMoney(data.prices.debt_free_purchase_price)}
                                        />
                                        <DetailField
                                            label="Ensisijaislaina"
                                            value={formatMoney(data.prices.primary_loan_amount)}
                                        />
                                        <DetailField
                                            label="Ensimmäinen ostopäivä"
                                            value={formatDate(data.prices.first_purchase_date)}
                                        />
                                        <DetailField
                                            label="Viimeisin ostopäivä"
                                            value={formatDate(data.prices.latest_purchase_date)}
                                        />
                                        <DetailField
                                            label="Rakennusaikaiset lainat"
                                            value={formatMoney(data.prices.construction.loans)}
                                        />
                                        <DetailField
                                            label="Rakennusaikaiset korot"
                                            value={formatMoney(data.prices.construction.interest)}
                                        />
                                        <DetailField
                                            label="Luovutushinta (RA)"
                                            value={formatMoney(data.prices.construction.debt_free_purchase_price)}
                                        />
                                        <DetailField
                                            label="Rakennusaikaiset lisätyöt"
                                            value={formatMoney(data.prices.construction.additional_work)}
                                        />
                                    </div>
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
                    title={"Asuntokohtaiset parannukset"}
                    editableType={"apartment"}
                />
                <QueryStateHandler
                    data={housingCompanyData}
                    error={housingCompanyError}
                    isLoading={housingCompanyIsLoading}
                >
                    <ImprovementsTable
                        data={housingCompanyData as IHousingCompanyDetails}
                        title={"Yhtiökohtaiset parannukset"}
                        editableType={"housingCompany"}
                        editPath={`/housing-companies/${housingCompanyData?.id}/improvements`}
                    />
                </QueryStateHandler>
            </div>
        </>
    );
};

const ApartmentDetailsPage = (): JSX.Element => {
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
                <LoadedApartmentDetails data={data as IApartmentDetails} />
            </QueryStateHandler>
        </div>
    );
};

export default ApartmentDetailsPage;
