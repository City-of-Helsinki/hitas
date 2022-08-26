import React from "react";

import {Card, IconLock, IconLockOpen, StatusLabel, Tabs} from "hds-react";
import {useParams} from "react-router";
import {Link} from "react-router-dom";

import {useGetApartmentDetailQuery} from "../../app/services";
import {DetailField, QueryStateHandler} from "../../common/components";
import {IApartmentDetails, IOwner} from "../../common/models";
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
    const {data, error, isLoading} = useGetApartmentDetailQuery(params.apartmentId as string);

    const LoadedApartmentDetails = ({data}: {data: IApartmentDetails}) => {
        return (
            <>
                <h1 className={"main-heading"}>
                    <Link to={`/housing-companies/${data.housing_company.id}`}>
                        <span className={"name"}>{data.housing_company.name}</span>
                        <span className="address">{formatAddress(data.address)}</span>
                        <StatusLabel>{data.state}</StatusLabel>
                    </Link>
                </h1>
                <h2 className={"apartment-stats"}>
                    <span className="apartment-stats--number">
                        {data.stair}
                        {data.apartment_number}
                    </span>
                    <span>{data.apartment_type.value}</span>
                    <span>{data.surface_area}m²</span>
                    <span>{data.floor}.krs</span>
                </h2>
                <div className="apartment-action-cards">
                    <Card>
                        <p>Vahvistamaton enimmäishinta</p>
                        <p className="price">210 000 €</p>
                        <p>Vahvistettu enimmäishinta</p>
                        <p className="price">-</p>
                    </Card>
                    <Card>
                        <label>Vahvistettu myyntiehto</label>
                        <SalesCondition
                            name="Arabian unelma (valm.2015)"
                            address="Arabiankatu 5 C 2, 00440"
                            url={`/housing-companies/${data.housing_company.id}`}
                            isConfirmed={true}
                        />
                        <label>Vahvistamaton myyntiehto</label>
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
                                            value={`${data.purchase_price} €`}
                                        />
                                        <DetailField
                                            label="Hankinta-arvo"
                                            value={`${data.acquisition_price} €`}
                                        />
                                        <DetailField
                                            label="Valmistumispäivä"
                                            value={data.date}
                                        />
                                    </div>
                                    <div className="columns">
                                        <div className="column">
                                            <label className="detail-field-label">Omistajat</label>
                                            {data.owners.map((owner: IOwner) => (
                                                <DetailField
                                                    key={owner.person.id}
                                                    label={`${owner.person.first_name} ${owner.person.last_name} ${owner.person.social_security_number}`}
                                                    value={`Omistusosuus: ${owner.ownership_percentage}%`}
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
                                                value={
                                                    data.share_number_start && data.share_number_end
                                                        ? data.share_number_end - data.share_number_start + 1
                                                        : 0
                                                }
                                            />
                                            <DetailField
                                                label="Osakkeet"
                                                value={`${data.share_number_start} - ${data.share_number_end}`}
                                            />
                                            <DetailField
                                                label="Luovutushinta"
                                                value={`${data.debt_free_purchase_price} €`}
                                            />
                                            <DetailField
                                                label="Ensisijaislaina"
                                                value={`${data.primary_loan_amount} €`}
                                            />
                                            <DetailField
                                                label="Rakennusaikaiset loans"
                                                value={`${data.loans_during_construction} €`}
                                            />
                                            <DetailField
                                                label="Rakennusaikaiset korot"
                                                value={`${data.interest_during_construction} €`}
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
