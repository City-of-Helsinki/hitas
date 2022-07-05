import { Tabs } from "hds-react";

const Company = () => {
    const theme = {
        "--tab-color": "var(--color-black-90)",
        "--tab-active-border-color": "var(--color-black-90)",
    };
    return (
        <div className="company">
            <h1 className="main-heading">Yhtiö</h1>
            <div className="company-details">
                <Tabs theme={theme}>
                    <Tabs.TabList>
                        <Tabs.Tab>Perustiedot</Tabs.Tab>
                        <Tabs.Tab>Lisätiedot</Tabs.Tab>
                        <Tabs.Tab>Dokumentit</Tabs.Tab>
                    </Tabs.TabList>
                    <Tabs.TabPanel>
                        <div className="company-details__tab basic-details">
                            <div className="column">
                                <label className="detail-label">
                                    Yhtiön hakunimi
                                </label>
                                <div className="detail-value">
                                    Aapeli Aava
                                </div>
                                <label className="detail-label">
                                    Yhtiön virallinen nimi
                                </label>
                                <div className="detail-value">
                                    Helsingin Aapeli Aava Oy
                                </div>
                                <label className="detail-label">
                                    Virallinen osoite
                                </label>
                                <div className="detail-value">
                                    Peipposentie 13, 00720, Helsinki
                                </div>
                                <label className="detail-label">
                                    Alue
                                </label>
                                <div className="detail-value">
                                    Helsinki 2: 30 - Pikkuhuopalahti
                                </div>
                                <label className="detail-label">
                                    Valmistumispäivä
                                </label>
                                <div className="detail-value">
                                    1.1.2015
                                </div>
                                <label className="detail-label">
                                    Hankinta-arvo
                                </label>
                                <div className="detail-value">
                                    10 500 000 €
                                </div>
                            </div>
                            <div className="column">
                                <label className="detail-label">
                                    Huomioitavaa
                                </label>
                                <textarea></textarea>
                            </div>
                        </div>
                    </Tabs.TabPanel>
                    <Tabs.TabPanel>
                        <div className="company-details__tab additional-details">
                            Lisätiedot
                        </div>
                    </Tabs.TabPanel>
                    <Tabs.TabPanel>
                        <div className="company-details__tab documents">
                            Dokumentit
                        </div>
                    </Tabs.TabPanel>
                </Tabs>
            </div>
        </div>
    );
};

export default Company;
