import React, {useState} from "react";

import {Button, Card, IconLock, IconLockOpen, StatusLabel, Tabs} from "hds-react";
import {useParams} from "react-router";
import {Link} from "react-router-dom";

import {useGetApartmentDetailQuery} from "../../app/services";
import {DetailField, QueryStateHandler} from "../../common/components";
import {IApartmentDetails, IOwnership} from "../../common/models";
import {formatAddress} from "../../common/utils";

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

const ApartmentDetailsPage = (): JSX.Element => {
    const params = useParams();
    const [priceMH] = useState(210000);
    const [priceRH] = useState(250000);
    const [priceRNH] = useState(130000);
    const {data, error, isLoading} = useGetApartmentDetailQuery({
        housingCompanyId: params.housingCompanyId as string,
        apartmentId: params.apartmentId as string,
    });

    const LoadedApartmentDetails = ({data}: {data}) => {
        return (
            <>
                <h1 className={"main-heading"}>
                    <Link to={`/housing-companies/${data.links.housing_company.id}`}>
                        <span className={"name"}>{data.links.housing_company.display_name}</span>
                        <span className="address">{formatAddress(data.address)}</span>
                        <StatusLabel>{data.state}</StatusLabel>
                    </Link>
                </h1>
                <h2 className={"apartment-stats"}>
                    <span className="apartment-stats--number">
                        {data.address.stair}
                        {data.address.apartment_number}
                    </span>
                    <span>
                        2 {/* TODO: Substitute with dynamic value once the API supplies one */}
                        {data.type.value}
                    </span>
                    <span>{data.surface_area}m²</span>
                    <span>{data.address.floor}.krs</span>
                </h2>
                <div className="apartment-action-cards">
                    <Card>
                        <label className="card-heading">Vahvistamaton enimmäishinta</label>
                        <div className="unconfirmed-prices">
                            <div className="price">
                                <span className="basis">Markkinahintaindeksi</span>
                                <span className="amount">
                                    <span className="value">{priceMH}</span> €
                                </span>
                            </div>
                            <div className="price price--current-top">
                                <span className="basis">Rakennushintaindeksi</span>
                                <span className="amount">
                                    <span className="value">{priceRH}</span> €
                                </span>
                            </div>
                            <div className="price">
                                <span className="basis">Rajaneliöhinta</span>
                                <span className="amount">
                                    <span className="value">{priceRNH}</span> €
                                </span>
                            </div>
                        </div>
                        <label className="card-heading">Vahvistettu enimmäishinta</label>
                        <p className="confirmed-price">250000€</p>
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
                                            value={`${data.prices.purchase_price} €`}
                                        />
                                        <DetailField
                                            label="Hankinta-arvo"
                                            value={`${data.prices.acquisition_price} €`}
                                        />
                                        <DetailField
                                            label="Valmistumispäivä"
                                            value={data.completion_date}
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
                                                            {`${ownership.owner.name}
                                                                (${ownership.owner.identifier})`}
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
                                                value={`${data.prices.debt_free_purchase_price} €`}
                                            />
                                            <DetailField
                                                label="Ensisijaislaina"
                                                value={`${data.prices.primary_loan_amount} €`}
                                            />
                                            <DetailField
                                                label="Rakennusaikaiset lainat"
                                                value={`${data.prices.construction.loans} €`}
                                            />
                                            <DetailField
                                                label="Rakennusaikaiset korot"
                                                value={`${data.prices.construction.interest} €`}
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
                    <div className="list__wrapper list-wrapper--upgrades">
                        <h2 className="detail-list__heading">Asuntokohtaiset parannukset</h2>
                        <ul className="detail-list__list">
                            <li className="detail-list__list-headers">
                                <div>Nimi</div>
                                <div>Summa</div>
                                <div>Valmistumispvm</div>
                            </li>
                            <li className="detail-list__list-item">
                                <div>Keittiöremontti</div>
                                <div>20 000 €</div>
                                <div>1.12.2021</div>
                            </li>
                        </ul>
                    </div>
                    <div className="list__wrapper list-wrapper--upgrades">
                        <h2 className="detail-list__heading">Yhtiökohtaiset parannukset</h2>
                        <ul className="detail-list__list">
                            <li className="detail-list__list-headers">
                                <div>Nimi</div>
                                <div>Summa</div>
                                <div>Valmistumispvm</div>
                                <div>Jakoperuste</div>
                            </li>
                            <li className="detail-list__list-item">
                                <div>Parvekelasien lisäys</div>
                                <div>340 000 €</div>
                                <div>1.1.2015</div>
                                <div>Neliöiden mukaan</div>
                            </li>
                            <li className="detail-list__list-item">
                                <div>Hissin rakennus</div>
                                <div>2 340 000 €</div>
                                <div>1.12.2021</div>
                                <div>Neliöiden mukaan</div>
                            </li>
                        </ul>
                    </div>
                </div>
            </>
        );
    };
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
