import {Button, IconPlus, StatusLabel, Tabs} from "hds-react";
import {Link} from "react-router-dom";

import React, {useContext, useState} from "react";
import {DetailField, EditButton, Heading, ImprovementsTable, MutateForm, MutateModal} from "../../common/components";
import {propertyManagerMutateFormProps} from "../../common/components/mutateComponents/mutateFormProps";
import {getHousingCompanyHitasTypeName, getHousingCompanyRegulationStatusName} from "../../common/localisation";
import {IPropertyManager} from "../../common/schemas";
import {formatAddress, formatDate, formatMoney} from "../../common/utils";
import {HousingCompanyApartmentResultsList} from "../apartment/ApartmentListPage";
import {BatchCompleteApartmentsModal} from "./";
import HousingCompanyViewContextProvider, {
    HousingCompanyViewContext,
} from "./components/HousingCompanyViewContextProvider";
import SalesCatalogImport from "./components/SalesCatalogImport";

const LoadedHousingCompanyDetails = (): React.JSX.Element => {
    const {housingCompany} = useContext(HousingCompanyViewContext);
    if (!housingCompany) throw new Error("Housing company not found");

    const [isModifyPropertyManagerModalVisible, setIsModifyPropertyManagerModalVisible] = useState(false);

    return (
        <>
            <Heading>
                {housingCompany.name.display}
                <div className="buttons">
                    <SalesCatalogImport />
                    <EditButton
                        state={{housingCompany: housingCompany}}
                        disabled={housingCompany.regulation_status !== "regulated"}
                    />
                </div>
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
                                                    {`${housingCompany.property_manager.name} (${
                                                        housingCompany.property_manager.email ?? ""
                                                    })`}
                                                </button>
                                            ) : (
                                                "-"
                                            )}
                                        </div>
                                    </div>
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
                <ImprovementsTable
                    data={housingCompany}
                    title="Yhtiökohtaiset parannukset"
                    editableType={housingCompany.regulation_status === "regulated" ? "housingCompany" : undefined}
                />
                <div style={{display: "flex", flexFlow: "row nowrap", gap: "var(--spacing-layout-s)"}}>
                    <div className="list-wrapper list-wrapper--real-estates">
                        <Heading type="list">
                            <span>Kiinteistöt</span>
                            <EditButton
                                pathname="real-estates"
                                state={{housingCompany: housingCompany}}
                                disabled={housingCompany.regulation_status !== "regulated"}
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
                                disabled={housingCompany.regulation_status !== "regulated"}
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
                        <div className="buttons">
                            <BatchCompleteApartmentsModal housingCompanyId={housingCompany.id} />
                            <Link to="apartments/create">
                                <Button
                                    theme="black"
                                    size="small"
                                    iconLeft={<IconPlus />}
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
            </div>
        </>
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
