import {IconAlertCircle, Tabs} from "hds-react";
import React, {useContext, useState} from "react";
import {DetailField, Divider, DocumentsTable, EditButton, Heading, ImprovementsTable} from "../../../common/components";
import {
    MutateForm,
    MutateModal,
    OwnerMutateForm,
    propertyManagerMutateFormProps,
} from "../../../common/components/mutateComponents";
import {IOwner, IOwnership, IPropertyManager} from "../../../common/schemas";
import {formatDate, formatMoney, formatOwner} from "../../../common/utils";
import {ApartmentViewContext, ApartmentViewContextProvider} from "../components/ApartmentViewContextProvider";
import {
    ApartmentConditionsOfSaleCard,
    ApartmentMaximumPricesCard,
    RemoveApartmentLatestSaleModalButton,
} from "./components";

const OwnerEditModalButton = ({owner}: {owner: IOwner}): React.JSX.Element => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    return (
        <>
            <button
                className="text-button"
                onClick={() => setIsModalOpen(true)}
            >
                {formatOwner(owner)}
            </button>
            <MutateModal
                defaultObject={owner}
                dialogTitles={{modify: "Muokkaa henkilötietoja"}}
                isVisible={isModalOpen}
                closeModalAction={() => setIsModalOpen(false)}
                MutateFormComponent={OwnerMutateForm}
            />
        </>
    );
};

const PropertyManagerEditModalButton = ({propertyManager}: {propertyManager: IPropertyManager}): React.JSX.Element => {
    const [isModalVisible, setIsModalVisible] = useState(false);

    return (
        <>
            <button
                className="text-button"
                onClick={() => setIsModalVisible(true)}
            >
                {propertyManager.name}
            </button>
            <MutateModal
                defaultObject={propertyManager}
                dialogTitles={{modify: "Muokkaa isännöitsijän tietoja"}}
                isVisible={isModalVisible}
                closeModalAction={() => setIsModalVisible(false)}
                MutateFormComponent={MutateForm}
                mutateFormProps={propertyManagerMutateFormProps}
            />
        </>
    );
};

const LoadedApartmentDetails = (): React.JSX.Element => {
    const {housingCompany, apartment} = useContext(ApartmentViewContext);
    if (!apartment) throw new Error("Apartment not found");

    // find out if apartment has owners with non-disclosure set to true
    const hasObfuscatedOwners = apartment.ownerships.some((ownership) => ownership.owner.non_disclosure);

    const alert = () => (
        <>
            <div className="alert-icon-background">
                <IconAlertCircle
                    className="alert-icon"
                    size="m"
                />
            </div>
            <span>Asunnossa turvakiellon alaisia omistajia</span>
        </>
    );
    return (
        <>
            <h2 className="apartment-stats">
                <span className="apartment-stats--number">
                    {apartment.address.stair}
                    {apartment.address.apartment_number}
                </span>
                <span>
                    {apartment.rooms ?? ""}
                    {apartment.type?.value ?? ""}
                </span>
                <span>{apartment.surface_area ? apartment.surface_area + "m²" : ""}</span>
                <span>{apartment.address.floor ? apartment.address.floor + ".krs" : ""}</span>
                {hasObfuscatedOwners && alert()}
            </h2>
            <div className="apartment-action-cards">
                <ApartmentMaximumPricesCard
                    apartment={apartment}
                    housingCompany={housingCompany}
                />
                <ApartmentConditionsOfSaleCard
                    apartment={apartment}
                    housingCompany={housingCompany}
                />
            </div>
            <div>
                <div className="tab-area">
                    <Tabs>
                        <Tabs.TabList className="tab-list">
                            <Tabs.Tab>Perustiedot</Tabs.Tab>
                            <Tabs.Tab>Dokumentit</Tabs.Tab>
                        </Tabs.TabList>
                        <Tabs.TabPanel>
                            <div className="apartment-details__tab">
                                <div className="row top-row">
                                    <DetailField
                                        label="Viimeisin kauppahinta"
                                        value={formatMoney(apartment.prices.latest_sale_purchase_price)}
                                        horizontal
                                    />
                                    <DetailField
                                        label="Hankinta-arvo"
                                        value={formatMoney(apartment.prices.first_sale_acquisition_price)}
                                        horizontal
                                    />
                                    <DetailField
                                        label="Valmistumispäivä"
                                        value={formatDate(apartment.completion_date)}
                                        horizontal
                                    />
                                </div>
                                <Divider size="l" />
                                <div className="columns">
                                    <div className="column">
                                        <div>
                                            <label className="detail-field-label">Omistajat</label>
                                            {apartment.ownerships.map((ownership: IOwnership) => (
                                                <div
                                                    key={ownership.owner.id}
                                                    className="detail-field-value"
                                                >
                                                    <OwnerEditModalButton owner={ownership.owner} />
                                                    <span> {ownership.percentage}%</span>
                                                </div>
                                            ))}
                                        </div>
                                        <div>
                                            <label className="detail-field-label">Isännöitsijä</label>
                                            <div className="detail-field-value">
                                                {housingCompany?.property_manager ? (
                                                    <PropertyManagerEditModalButton
                                                        propertyManager={housingCompany.property_manager}
                                                    />
                                                ) : (
                                                    "-"
                                                )}
                                            </div>
                                        </div>
                                        <DetailField
                                            label="Osakkeet"
                                            value={
                                                apartment.shares
                                                    ? `${apartment.shares.start} - ${apartment.shares.end} (${apartment.shares.total} kpl)`
                                                    : undefined
                                            }
                                        />
                                        <div>
                                            <label className="detail-field-label">Huomioitavaa</label>
                                            <textarea
                                                placeholder="Ei huomioitavaa"
                                                value={apartment.notes || ""}
                                                readOnly
                                            />
                                        </div>
                                    </div>
                                    <div className="column">
                                        <div className="row">
                                            <DetailField
                                                label="Viimeisin kauppapäivä"
                                                value={formatDate(apartment.prices.latest_purchase_date)}
                                            />
                                            {apartment.prices.latest_purchase_date && (
                                                <RemoveApartmentLatestSaleModalButton />
                                            )}
                                        </div>
                                        <Divider size="s" />
                                        <div className="row">
                                            <DetailField
                                                label="Ensimmäinen kauppapäivä"
                                                value={formatDate(apartment.prices.first_purchase_date)}
                                            />
                                            {!apartment.prices.latest_purchase_date && (
                                                <RemoveApartmentLatestSaleModalButton />
                                            )}
                                        </div>
                                        <DetailField
                                            label="Ensimmäinen kauppahinta"
                                            value={formatMoney(apartment.prices.first_sale_purchase_price)}
                                        />
                                        <DetailField
                                            label="Ensisijaislaina"
                                            value={formatMoney(
                                                apartment.prices.first_sale_share_of_housing_company_loans
                                            )}
                                        />

                                        <Divider size="s" />

                                        <DetailField
                                            label="Rakennusaikaiset lisätyöt"
                                            value={formatMoney(apartment.prices.construction.additional_work)}
                                        />
                                        <DetailField
                                            label="Rakennusaikaiset korot (MHI)"
                                            value={
                                                apartment.prices.construction.interest
                                                    ? formatMoney(apartment.prices.construction.interest.rate_mpi)
                                                    : 0
                                            }
                                        />
                                        <DetailField
                                            label="Rakennusaikaiset korot (RKI)"
                                            value={
                                                apartment.prices.construction.interest
                                                    ? formatMoney(apartment.prices.construction.interest.rate_cpi)
                                                    : 0
                                            }
                                        />
                                        {apartment.prices.construction.loans ? (
                                            <DetailField
                                                label="Rakennusaikaiset lainat"
                                                value={formatMoney(apartment.prices.construction.loans)}
                                            />
                                        ) : null}
                                        {apartment.prices.construction.debt_free_purchase_price ? (
                                            <DetailField
                                                label="Luovutushinta (RA)"
                                                value={formatMoney(
                                                    apartment.prices.construction.debt_free_purchase_price
                                                )}
                                            />
                                        ) : null}

                                        {apartment.prices.catalog_purchase_price ||
                                        apartment.prices.catalog_share_of_housing_company_loans ? (
                                            <>
                                                <Divider size="s" />
                                                <DetailField
                                                    label="Myyntihintaluettelon luovutushinta"
                                                    value={formatMoney(apartment.prices.catalog_purchase_price)}
                                                />
                                                <DetailField
                                                    label="Myyntihintaluettelon ensisijaislaina"
                                                    value={formatMoney(
                                                        apartment.prices.catalog_share_of_housing_company_loans
                                                    )}
                                                />
                                                <DetailField
                                                    label="Myyntihintaluettelon Hankinta-arvo"
                                                    value={formatMoney(apartment.prices.catalog_acquisition_price)}
                                                />
                                            </>
                                        ) : null}
                                    </div>
                                </div>
                            </div>
                        </Tabs.TabPanel>
                        <Tabs.TabPanel>
                            <div className="apartment-details__tab documents">
                                <Heading type="list">
                                    <span>Dokumentit</span>
                                    <EditButton pathname="documents" />
                                </Heading>
                                {apartment.documents?.length ? (
                                    <DocumentsTable parentObject={apartment} />
                                ) : (
                                    "Ei dokumentteja"
                                )}
                            </div>
                        </Tabs.TabPanel>
                    </Tabs>
                </div>
                {
                    // Half-Hitas and New Hitas apartments don't have any improvements so the table can be hidden
                    (housingCompany.hitas_type !== "half_hitas" && !housingCompany.new_hitas) ||
                    apartment.improvements.market_price_index.length ||
                    apartment.improvements.construction_price_index.length ? (
                        <ImprovementsTable
                            data={apartment}
                            title="Asuntokohtaiset parannukset"
                            isEditable={housingCompany.regulation_status === "regulated"}
                        />
                    ) : null
                }
                {housingCompany.hitas_type !== "half_hitas" ? (
                    <ImprovementsTable
                        data={housingCompany}
                        title="Yhtiökohtaiset parannukset"
                        isEditable={housingCompany.regulation_status === "regulated"}
                        editPath={`/housing-companies/${housingCompany.id}/improvements`}
                    />
                ) : null}
            </div>
        </>
    );
};

const ApartmentDetailsPage = (): React.JSX.Element => {
    return (
        <ApartmentViewContextProvider viewClassName="view--apartment-details">
            <LoadedApartmentDetails />
        </ApartmentViewContextProvider>
    );
};

export default ApartmentDetailsPage;
