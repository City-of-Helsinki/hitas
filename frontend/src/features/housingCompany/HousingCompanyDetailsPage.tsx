import {Button, Dialog, IconPlus, StatusLabel, Tabs} from "hds-react";
import {Link, useParams} from "react-router-dom";

import {useState} from "react";
import {useForm} from "react-hook-form";
import {
    useCreateFromSalesCatalogMutation,
    useGetHousingCompanyDetailQuery,
    useValidateSalesCatalogMutation,
} from "../../app/services";
import {
    CloseButton,
    DetailField,
    EditButton,
    Heading,
    ImprovementsTable,
    MutateForm,
    MutateModal,
    QueryStateHandler,
    SaveButton,
} from "../../common/components";
import {FileInput} from "../../common/components/form";
import {propertyManagerMutateFormProps} from "../../common/components/mutateComponents/mutateFormProps";
import {getHousingCompanyHitasTypeName, getHousingCompanyRegulationStatusName} from "../../common/localisation";
import {IHousingCompanyDetails, IPropertyManager, ISalesCatalogApartment} from "../../common/schemas";
import {formatAddress, formatDate, formatMoney, hdsToast} from "../../common/utils";
import {HousingCompanyApartmentResultsList} from "../apartment/ApartmentListPage";
import {BatchCompleteApartmentsModal} from "./";

const LoadedHousingCompanyDetails = ({housingCompany}: {housingCompany: IHousingCompanyDetails}): JSX.Element => {
    const [isImportModalOpen, setIsImportModalOpen] = useState(false);
    const [isModifyPropertyManagerModalVisible, setIsModifyPropertyManagerModalVisible] = useState(false);
    const params = useParams() as {readonly housingCompanyId: string};
    const salesCatalogForm = useForm({defaultValues: {salesCatalog: null}});
    const [validateSalesCatalog, {data: validateData, isLoading: isValidating, error: validateError}] =
        useValidateSalesCatalogMutation();
    const [createImportedApartments, {error: createError}] = useCreateFromSalesCatalogMutation();
    const {handleSubmit} = salesCatalogForm;
    const handleCreateButton = () => {
        const importedApartments: object[] = [];
        validateData.apartments.forEach((apartment: ISalesCatalogApartment) => {
            importedApartments.push({
                stair: apartment.stair,
                floor: apartment.floor,
                apartment_number: apartment.apartment_number,
                rooms: apartment.rooms,
                apartment_type: (apartment.apartment_type as {id: string}).id,
                surface_area: apartment.surface_area,
                share_number_start: apartment.share_number_start,
                share_number_end: apartment.share_number_end,
                catalog_purchase_price: apartment.catalog_purchase_price,
                catalog_primary_loan_amount: apartment.catalog_primary_loan_amount,
            });
        });
        createImportedApartments({
            data: importedApartments,
            housingCompanyId: params.housingCompanyId,
        })
            .then(() => {
                hdsToast.success("Asuntojen tuonti onnistui.");
                setIsImportModalOpen(false);
            })
            .catch((e) => {
                hdsToast.error("Asuntojen tuonti epäonnistui: " + e.message);
                // eslint-disable-next-line no-console
                console.warn(e, createError);
            });
    };
    const onSubmit = (data) => {
        validateSalesCatalog({
            data: data.salesCatalog,
            housingCompanyId: params.housingCompanyId,
        })
            .then(() => {
                setIsImportModalOpen(true);
            })
            // eslint-disable-next-line no-console
            .catch((e) => console.warn(e));
    };

    return (
        <>
            <Heading>
                {housingCompany.name.display}
                <form
                    className="buttons"
                    onSubmit={handleSubmit(onSubmit)}
                >
                    <FileInput
                        name="salesCatalog"
                        formObject={salesCatalogForm}
                        accept=".xlsx"
                        buttonLabel="Lataa myyntihintaluettelo"
                        onChange={() => onSubmit(salesCatalogForm.getValues())}
                    />
                    <EditButton
                        state={{housingCompany: housingCompany}}
                        disabled={housingCompany.regulation_status !== "regulated"}
                    />
                </form>
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
                                        value={formatDate(housingCompany.date)}
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
                            <BatchCompleteApartmentsModal housingCompanyId={params.housingCompanyId} />
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
                        <HousingCompanyApartmentResultsList housingCompanyId={params.housingCompanyId} />
                    </div>
                </div>
            </div>
            <Dialog
                id="import-sales-catalog-modal"
                aria-labelledby="Sales catalog import modal"
                isOpen={isImportModalOpen}
            >
                <Dialog.Header
                    id="import-sales-catalog-modal"
                    title="Myyntihintaluettelo"
                />
                <Dialog.Content>
                    <p>Luodaanko myyntihintaluettelon pohjalta seuraavat asunnot:</p>
                    <QueryStateHandler
                        data={validateData}
                        error={validateError}
                        isLoading={isValidating}
                    >
                        <div className="sales-catalog-import-list">
                            <div className="list-headers">
                                <div>Porras</div>
                                <div>Huoneisto</div>
                                <div>Kerros</div>
                                <div>Tyyppi</div>
                                <div>Pinta-ala</div>
                                <div>Osakenumerot</div>
                            </div>
                            {validateData && validateData?.apartments.length > 0 && (
                                <ul>
                                    {validateData?.apartments.map((apartment: ISalesCatalogApartment) => (
                                        <li key={apartment.row.toString()}>
                                            <div>{apartment.stair}</div>
                                            <div>{apartment.apartment_number}</div>
                                            <div>{apartment.floor}</div>
                                            <div>
                                                {apartment.rooms} {(apartment.apartment_type as {value: string}).value}
                                            </div>
                                            <div>{apartment.surface_area}</div>
                                            <div>{`${apartment.share_number_start} - ${apartment.share_number_end}`}</div>
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    </QueryStateHandler>
                </Dialog.Content>
                <Dialog.ActionButtons>
                    <CloseButton onClick={() => setIsImportModalOpen(false)} />
                    <SaveButton
                        onClick={() => handleCreateButton()}
                        buttonText="Luo asunnot"
                    />
                </Dialog.ActionButtons>
            </Dialog>
        </>
    );
};

const HousingCompanyDetailsPage = () => {
    const params = useParams() as {readonly housingCompanyId: string};
    const {data, error, isLoading} = useGetHousingCompanyDetailQuery(params.housingCompanyId);

    return (
        <div className="view--housing-company-details">
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <LoadedHousingCompanyDetails housingCompany={data as IHousingCompanyDetails} />
            </QueryStateHandler>
        </div>
    );
};

export default HousingCompanyDetailsPage;
