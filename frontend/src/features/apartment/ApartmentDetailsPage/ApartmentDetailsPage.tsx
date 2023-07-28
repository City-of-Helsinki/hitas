import {Tabs} from "hds-react";
import React, {useContext, useState} from "react";
import {DetailField, Divider, ImprovementsTable} from "../../../common/components";
import {
    MutateForm,
    MutateModal,
    OwnerMutateForm,
    propertyManagerMutateFormProps,
} from "../../../common/components/mutateComponents";
import {IOwner, IOwnership, IPropertyManager} from "../../../common/schemas";
import {formatDate, formatMoney} from "../../../common/utils";
import {ApartmentViewContext, ApartmentViewContextProvider} from "../components/ApartmentViewContextProvider";
import {
    ApartmentConditionsOfSaleCard,
    ApartmentMaximumPricesCard,
    RemoveApartmentLatestSaleModalButton,
} from "./components";

const LoadedApartmentDetails = (): React.JSX.Element => {
    const {housingCompany, apartment} = useContext(ApartmentViewContext);
    if (!apartment) throw new Error("Apartment not found");

    // Handle visibility of the relevant modals
    const [isModifyOwnerModalVisible, setIsModifyOwnerModalVisible] = useState(false);
    const [isModifyPropertyManagerModalVisible, setIsModifyPropertyManagerModalVisible] = useState(false);

    const [owner, setOwner] = useState<IOwner | undefined>(undefined);
    const modifyOwnerHandler = (selectedOwner: IOwner) => {
        setIsModifyOwnerModalVisible(true);
        setOwner(selectedOwner);
    };

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
                                                    <button
                                                        className="text-button"
                                                        onClick={() => modifyOwnerHandler(ownership.owner)}
                                                    >
                                                        {ownership.owner.name} ({ownership.owner.identifier})
                                                    </button>
                                                    <span> {ownership.percentage}%</span>
                                                </div>
                                            ))}
                                        </div>
                                        <div>
                                            <label className="detail-field-label">Isännöitsijä</label>
                                            <div className="detail-field-value">
                                                {housingCompany?.property_manager ? (
                                                    <button
                                                        className="text-button"
                                                        onClick={() => setIsModifyPropertyManagerModalVisible(true)}
                                                    >
                                                        {housingCompany?.property_manager?.name || " "}
                                                    </button>
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
                                            label="Rakennusaikaiset korot (6 %)"
                                            value={
                                                apartment.prices.construction.interest
                                                    ? formatMoney(apartment.prices.construction.interest.rate_6)
                                                    : 0
                                            }
                                        />
                                        <DetailField
                                            label="Rakennusaikaiset korot (14 %)"
                                            value={
                                                apartment.prices.construction.interest
                                                    ? formatMoney(apartment.prices.construction.interest.rate_14)
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
                            <div className="apartment-details__tab documents">Dokumentit</div>
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
            <MutateModal
                // Modify owner modal
                defaultObject={owner as IOwner}
                dialogTitles={{modify: "Muokkaa henkilötietoja"}}
                isVisible={isModifyOwnerModalVisible}
                closeModalAction={() => setIsModifyOwnerModalVisible(false)}
                MutateFormComponent={OwnerMutateForm}
            />
            <MutateModal
                // Modify property manager modal
                defaultObject={housingCompany?.property_manager as IPropertyManager}
                dialogTitles={{modify: "Muokkaa isännöitsijän tietoja"}}
                isVisible={isModifyPropertyManagerModalVisible}
                closeModalAction={() => setIsModifyPropertyManagerModalVisible(false)}
                MutateFormComponent={MutateForm}
                mutateFormProps={propertyManagerMutateFormProps}
            />
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
