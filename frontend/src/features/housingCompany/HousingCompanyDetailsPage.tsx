import {StatusLabel, Tabs} from "hds-react";
import {DetailField} from "../../common/components";

const HousingCompanyDetailsPage = () => {
    const theme = {
        "--tab-color": "var(--color-black-90)",
        "--tab-active-border-color": "var(--color-black-90)",
    };
    return (
        <div className="company">
            <h1 className="main-heading">Aapeli Aava</h1>
            <div className="company-status">
                <StatusLabel>Vapautunut 1.6.2022</StatusLabel>
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
                                    <Detail
                                        label="Yhtiön hakunimi"
                                        value="Aapeli Aava"
                                    />
                                    <Detail
                                        label="Yhtiön virallinen nimi"
                                        value="Helsingin Aapelin Aava Oy"
                                    />
                                    <Detail
                                        label="Virallinen osoite"
                                        value="Peipposentie 13, 00720, Helsinki"
                                    />
                                    <Detail
                                        label="Alue"
                                        value="Helsinki 2: 30 Pikkuhuopalahti"
                                    />
                                    <Detail
                                        label="Valmistumispäivä"
                                        value="1.1.2015"
                                    />
                                    <Detail
                                        label="Hankinta-arvo"
                                        value="10 500 000 €"
                                    />
                                </div>
                                <div className="column">
                                    <label className="detail-label">Huomioitavaa</label>
                                    <textarea></textarea>
                                </div>
                            </div>
                        </Tabs.TabPanel>
                        <Tabs.TabPanel>
                            <div className="company-details__tab additional-details">
                                <div className="column">
                                    <Detail
                                        label="Y-tunnus"
                                        value="123456-12"
                                    />
                                    <Detail
                                        label="Huoneistojen lukumäärä"
                                        value="120"
                                    />
                                    <Detail
                                        label="Huoneistojen pinta-ala"
                                        value="2 045 m²"
                                    />
                                    <Detail
                                        label="Rakennuttaja"
                                        value="Realia"
                                    />
                                </div>
                                <div className="column">
                                    <Detail
                                        label="Isännöitsijä"
                                        value="Hemmo Perusdude (044 2366 636)"
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
                    <p>Coming up - the listing will be added once the component for an apartments listing is done</p>
                </div>
            </div>
        </div>
    );
};

export default HousingCompanyDetailsPage;
