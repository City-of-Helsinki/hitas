import {
    Button,
    ButtonPresetTheme,
    ButtonSize,
    ButtonVariant,
    IconAngleDown,
    IconAngleUp,
    IconPlus,
    IconSize,
    Tabs,
} from "hds-react";
import {Link} from "react-router-dom";

import React, {useContext, useState} from "react";
import {
    DetailField,
    DocumentsTable,
    DownloadButton,
    EditButton,
    Heading,
    ImprovementsTable,
} from "../../common/components";
import {MutateForm, MutateModal, propertyManagerMutateFormProps} from "../../common/components/mutateComponents";
import {IPropertyManager} from "../../common/schemas";
import {formatAddress, formatDate, formatMoney} from "../../common/utils";
import {HousingCompanyApartmentResultsList} from "../apartment/ApartmentListPage";
import {BatchCompleteApartmentsModal} from "./";
import {
    HousingCompanyViewContext,
    HousingCompanyViewContextProvider,
} from "./components/HousingCompanyViewContextProvider";
import SalesCatalogImport from "./components/SalesCatalogImport";
import {downloadHousingCompanyApartmentsExcel, downloadHousingCompanyWithOwnersExcel} from "../../common/services";
import HousingCompanyOwnersTable from "../../common/components/HousingCompanyOwnersTable";

const LoadedHousingCompanyDetails = (): React.JSX.Element => {
    const {housingCompany} = useContext(HousingCompanyViewContext);
    if (!housingCompany) throw new Error("Housing company not found");

    const [isModifyPropertyManagerModalVisible, setIsModifyPropertyManagerModalVisible] = useState(false);
    const [isHousingCompanyOwnersTableVisible, setIsHousingCompanyOwnersTableVisible] = useState(false);

    return (
        <div className="company-details">
            <div className="tab-area">
                <Tabs>
                    <Tabs.TabList className="tab-list">
                        <Tabs.Tab>Perustiedot</Tabs.Tab>
                        <Tabs.Tab>Lisätiedot</Tabs.Tab>
                        <Tabs.Tab>Dokumentit</Tabs.Tab>
                    </Tabs.TabList>
                    <Tabs.TabPanel>
                        <div className="company-details__tab">
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
                                    value={formatDate(housingCompany.completion_date)}
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
                                <div>
                                    <label className="detail-field-label">Isännöitsijä</label>
                                    <div className="detail-field-value">
                                        {housingCompany.property_manager ? (
                                            <button
                                                className="text-button"
                                                onClick={() => setIsModifyPropertyManagerModalVisible(true)}
                                            >
                                                {housingCompany.property_manager.name}
                                                {housingCompany.property_manager.email
                                                    ? ` (${housingCompany.property_manager.email})`
                                                    : ""}
                                            </button>
                                        ) : (
                                            "-"
                                        )}
                                        {housingCompany.property_manager ? (
                                            <div className="detail-field-metadata">
                                                Vaihdettu:{" "}
                                                {housingCompany.property_manager_changed_at
                                                    ? formatDate(housingCompany.property_manager_changed_at)
                                                    : "tieto puuttuu"}
                                                , muokattu:{" "}
                                                {housingCompany.property_manager.modified_at
                                                    ? formatDate(housingCompany.property_manager.modified_at)
                                                    : "tieto puuttuu"}
                                            </div>
                                        ) : null}
                                    </div>
                                </div>
                                <div>
                                    <label className="detail-field-label">Huomioitavaa</label>
                                    <textarea
                                        placeholder="Ei huomioitavaa"
                                        readOnly
                                        value={housingCompany.notes || ""}
                                    />
                                </div>
                                <SalesCatalogImport />
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
                        <div className="company-details__tab documents">
                            <Heading type="list">
                                <span>Dokumentit</span>
                                <EditButton pathname="documents" />
                            </Heading>
                            {housingCompany.documents?.length ? (
                                <DocumentsTable parentObject={housingCompany} />
                            ) : (
                                "Ei dokumentteja"
                            )}
                        </div>
                    </Tabs.TabPanel>
                </Tabs>
                <MutateModal
                    // Modify property manager modal
                    defaultObject={housingCompany?.property_manager as IPropertyManager}
                    dialogTitles={{modify: "Muokkaa isännöitsijän tietoja"}}
                    isVisible={isModifyPropertyManagerModalVisible}
                    closeModalAction={() => setIsModifyPropertyManagerModalVisible(false)}
                    MutateFormComponent={MutateForm}
                    mutateFormProps={propertyManagerMutateFormProps}
                />
            </div>
            {housingCompany.hitas_type !== "half_hitas" ? (
                <ImprovementsTable
                    data={housingCompany}
                    title="Yhtiökohtaiset parannukset"
                    isEditable={housingCompany.regulation_status === "regulated"}
                />
            ) : null}
            <div style={{display: "flex", flexFlow: "row nowrap", gap: "var(--spacing-layout-s)"}}>
                <div className="list-wrapper list-wrapper--real-estates">
                    <Heading type="list">
                        <span>Kiinteistöt</span>
                        <EditButton pathname="real-estates" />
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
                        <EditButton pathname="buildings" />
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
                    <div className="buttons">
                        <DownloadButton
                            buttonText="Lataa raportti"
                            onClick={() => downloadHousingCompanyApartmentsExcel(housingCompany.id)}
                            size="small"
                            variant={ButtonVariant.Secondary}
                        />
                        <BatchCompleteApartmentsModal housingCompany={housingCompany} />
                        <Link to="apartments/create">
                            <Button
                                theme={ButtonPresetTheme.Black}
                                size={ButtonSize.Small}
                                iconStart={<IconPlus />}
                                disabled={housingCompany.regulation_status !== "regulated"}
                            >
                                Lisää asunto
                            </Button>
                        </Link>
                    </div>
                </Heading>
                <div className="listing">
                    <HousingCompanyApartmentResultsList housingCompanyId={housingCompany.id} />
                </div>
            </div>
            {housingCompany.regulation_status === "regulated" && (
                <div className="list-wrapper list-wrapper--owners">
                    <Heading type="list">
                        <button
                            className="text-button"
                            onClick={() => {
                                isHousingCompanyOwnersTableVisible
                                    ? setIsHousingCompanyOwnersTableVisible(false)
                                    : setIsHousingCompanyOwnersTableVisible(true);
                            }}
                        >
                            Omistajat
                            {isHousingCompanyOwnersTableVisible ? (
                                <IconAngleUp size={IconSize.Medium} />
                            ) : (
                                <IconAngleDown size={IconSize.Medium} />
                            )}
                        </button>
                        <div className="buttons">
                            <DownloadButton
                                buttonText="Lataa raportti"
                                onClick={() => downloadHousingCompanyWithOwnersExcel(housingCompany.id)}
                                size="small"
                            />
                        </div>
                    </Heading>
                    {isHousingCompanyOwnersTableVisible && (
                        <HousingCompanyOwnersTable housingCompanyId={housingCompany.id} />
                    )}
                </div>
            )}
        </div>
    );
};

const HousingCompanyDetailsPage = () => {
    return (
        <HousingCompanyViewContextProvider viewClassName="view--housing-company-details">
            <LoadedHousingCompanyDetails />
        </HousingCompanyViewContextProvider>
    );
};

export default HousingCompanyDetailsPage;
