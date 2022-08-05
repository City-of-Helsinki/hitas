import React from "react";

import {StatusLabel, Tabs} from "hds-react";
import {useParams} from "react-router";
import {Link} from "react-router-dom";

import {useGetApartmentDetailQuery} from "../../app/services";
import {DetailField, QueryStateHandler} from "../../common/components";
import {IApartmentDetails, IOwner} from "../../common/models";
import {formatAddress} from "../../common/utils";

const ApartmentDetailsPage = () => {
    const params = useParams();
    const {data, error, isLoading} = useGetApartmentDetailQuery(params.apartmentId as string);

    const LoadedApartmentDetails = ({data}: {data: IApartmentDetails}) => {
        return (
            <>
                <h1>
                    <Link to={`/housing-companies/${data.housing_company.id}`}>
                        {data.housing_company.name} {formatAddress(data.address)}
                    </Link>
                </h1>
                <h2>
                    {data.stair}
                    {data.apartment_number}
                </h2>
                <h2>
                    {data.apartment_type.value} | {data.surface_area}m² | {data.floor}.krs
                </h2>
                <div className="apartment-status">
                    <StatusLabel>{data.state}</StatusLabel>
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
                                            label="Kauppakirjahinta"
                                            value={`${data.purchase_price} €`}
                                        />
                                        <DetailField
                                            label="Hankinta-arvo"
                                            value={`${data.acquisition_price} €`}
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
                                        <DetailField
                                            label="Valmistumispäivä"
                                            value={data.date}
                                        />
                                        <DetailField
                                            label="Isännöitsijä"
                                            value="TODO"
                                        />
                                        <label className="detail-field-label">Omistajat</label>
                                        {data.owners.map((owner: IOwner) => (
                                            <DetailField
                                                key={owner.person.id}
                                                label={`${owner.person.first_name} ${owner.person.last_name} ${owner.person.social_security_number}`}
                                                value={`Omistusosuus: ${owner.ownership_percentage}%`}
                                            />
                                        ))}
                                    </div>
                                    <div className="column">
                                        <label className="detail-field-label">Huomioitavaa</label>
                                        <textarea
                                            readOnly
                                            value={data.notes as string}
                                        ></textarea>
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
        <div className="apartment">
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
