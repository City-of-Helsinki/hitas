import {StatusLabel, Tabs} from "hds-react";
import {useParams} from "react-router";

import {useGetHousingCompanyDetailQuery} from "../../app/services";
import {DetailField} from "../../common/components";

const HousingCompanyDetailsPage = () => {
    const params = useParams();
    const {data, error, isLoading} = useGetHousingCompanyDetailQuery(params.housingCompanyId as string);

    const theme = {
        "--tab-color": "var(--color-black-90)",
        "--tab-active-border-color": "var(--color-black-90)",
    };

    if (isLoading || error || !data) {
        return (
            <div className="company">
                <h1 className="main-heading">Loading...</h1>
            </div>
        );
    } else {
        return (
            <div className="company">
                <h1 className="main-heading">{data.name.display}</h1>
                <div className="company-status">
                    <StatusLabel>Vapautunut 1.6.2022 ({data.state})</StatusLabel>
                </div>
                <div className="company-details">
                    <div className="tab-area">
                        <Tabs theme={theme}>
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
                                            value={`${data.address.street}, ${data.address.postal_code}, ${data.address.city}`}
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
                                            value={`${data.acquisition_price?.realized} €`} // TODO: Format number
                                        />
                                    </div>
                                    <div className="column">
                                        <label className="detail-field-label">Huomioitavaa</label>
                                        <textarea>{data.notes}</textarea>
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
                                            label="Huoneistojen lukumäärä"
                                            value="120"
                                        />
                                        <DetailField
                                            label="Huoneistojen pinta-ala"
                                            value="2 045 m²"
                                        />
                                        <DetailField
                                            label="Rakennuttaja"
                                            value={data.developer?.value}
                                        />
                                    </div>
                                    <div className="column">
                                        <DetailField
                                            label="Isännöitsijä"
                                            value={`${data.property_manager?.name} (${data.property_manager?.email})`}
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
                    <div>
                        <h2>Asunnot</h2>
                        <p>
                            Coming up - the listing will be added once the component for an apartments listing is done
                        </p>
                    </div>
                </div>
            </div>
        );
    }
};

export default HousingCompanyDetailsPage;
