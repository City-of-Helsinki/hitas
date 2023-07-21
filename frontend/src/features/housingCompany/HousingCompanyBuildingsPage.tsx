import React, {useContext, useRef, useState} from "react";

import {Button, IconPlus, IconTrash, Table} from "hds-react";

import {zodResolver} from "@hookform/resolvers/zod";
import {useForm} from "react-hook-form";
import {DeleteButton, GenericActionModal, Heading, NavigateBackButton} from "../../common/components";
import {FormProviderForm, SaveFormButton, SelectInput, TextInput} from "../../common/components/forms";
import {IBuilding, IBuildingWritable, IRealEstate, WritableBuildingSchema} from "../../common/schemas";
import {useDeleteBuildingMutation, useSaveBuildingMutation} from "../../common/services";
import {hdsToast, setAPIErrorsForFormFields} from "../../common/utils";
import {
    HousingCompanyViewContext,
    HousingCompanyViewContextProvider,
} from "./components/HousingCompanyViewContextProvider";

const tableTheme = {
    "--header-background-color": "var(--color-engel-medium-light)",
};

const blankForm: IBuildingWritable = {
    real_estate_id: null,
    address: {
        street_address: "",
    },
    building_identifier: "",
};

interface IAnnotatedBuilding extends IBuilding {
    real_estate: Omit<IRealEstate, "buildings">;
}

const ModifyBuildingButton = ({building}: {building?: IAnnotatedBuilding}) => {
    const {housingCompany} = useContext(HousingCompanyViewContext);
    if (!housingCompany) throw new Error("Housing company not found");

    const isEditing = building !== undefined;

    const formRef = useRef<HTMLFormElement>(null);
    const formObject = useForm({
        defaultValues: isEditing ? {...building, real_estate_id: building.real_estate.id} : blankForm,
        mode: "all",
        resolver: zodResolver(WritableBuildingSchema),
    });

    const [isModalOpen, setIsModalOpen] = useState(false);
    const closeModal = () => {
        setIsModalOpen(false);
        formObject.reset();
    };

    const [saveBuilding, {isLoading}] = useSaveBuildingMutation();

    const onSubmit = (data) => {
        const realEstateId = isEditing ? building.real_estate.id : data.real_estate_id;
        saveBuilding({housingCompanyId: housingCompany.id, realEstateId: realEstateId, data: data})
            .unwrap()
            .then(() => {
                hdsToast.info("Rakennus luotu onnistuneesti.");
                setIsModalOpen(false);
                if (!isEditing) formObject.reset();
            })
            .catch((error) => {
                hdsToast.error("Rakennuksen luominen epäonnistui!");
                setAPIErrorsForFormFields(formObject, error);
            });
    };

    const realEstateOptions = housingCompany.real_estates.map((realEstate) => {
        return {
            label: `${realEstate.address.street_address} (${realEstate.property_identifier})`,
            value: realEstate.id,
        };
    });

    return (
        <>
            <Button
                theme="black"
                iconLeft={<IconPlus />}
                onClick={() => setIsModalOpen(true)}
                size={isEditing ? "small" : "default"}
            >
                {isEditing ? "Muokkaa" : "Lisää uusi"}
            </Button>

            <GenericActionModal
                title={isEditing ? "Muokkaa rakennuksen tietoja" : "Uusi rakennus"}
                modalIcon={<IconPlus />}
                isModalOpen={isModalOpen}
                closeModal={closeModal}
                confirmButton={
                    <SaveFormButton
                        formRef={formRef}
                        isLoading={isLoading}
                    />
                }
            >
                <FormProviderForm
                    formObject={formObject}
                    formRef={formRef}
                    onSubmit={onSubmit}
                >
                    <SelectInput
                        label="Kiinteistö"
                        name="real_estate_id"
                        options={realEstateOptions}
                        setDirectValue
                        required
                    />
                    <TextInput
                        label="Katuosoite"
                        name="address.street_address"
                        required
                    />
                    <TextInput
                        label="Rakennustunnus"
                        name="building_identifier"
                        tooltipText='Esimerkkiarvo: "123456789A"'
                    />
                </FormProviderForm>
            </GenericActionModal>
        </>
    );
};

const DeleteBuildingButton = ({building}: {building: IAnnotatedBuilding}) => {
    const {housingCompany} = useContext(HousingCompanyViewContext);
    if (!housingCompany) throw new Error("Housing company not found");

    const [isModalOpen, setIsModalOpen] = useState(false);
    const closeModal = () => setIsModalOpen(false);

    const [deleteBuilding, {isLoading}] = useDeleteBuildingMutation();

    const handleDeleteRealEstate = () => {
        deleteBuilding({housingCompanyId: housingCompany.id, realEstateId: building.real_estate.id, id: building.id})
            .unwrap()
            .then(() => {
                hdsToast.info("Rakennus poistettu onnistuneesti!");
                setIsModalOpen(false);
            })
            .catch((e) => {
                hdsToast.error("Myyntiehdon poistaminen epäonnistui!");
                // eslint-disable-next-line no-console
                console.warn(e);
            });
    };

    return (
        <>
            <DeleteButton
                onClick={() => setIsModalOpen(true)}
                isLoading={isLoading}
                size="small"
            />
            <GenericActionModal
                title="Poista rakennus"
                modalIcon={<IconTrash />}
                isModalOpen={isModalOpen}
                closeModal={closeModal}
                confirmButton={
                    <DeleteButton
                        onClick={handleDeleteRealEstate}
                        isLoading={isLoading}
                    />
                }
            >
                <p>
                    Haluatko varmasti poistaa rakennuksen '{building.address.street_address}{" "}
                    {building.building_identifier ? `(${building.building_identifier})` : ""}'?
                </p>
            </GenericActionModal>
        </>
    );
};

const buildingTableColumns = [
    {key: "id", headerName: "Not rendered"},
    {
        key: "real_estate",
        headerName: "Kiinteistö",
        transform: (obj: IAnnotatedBuilding) => obj.real_estate.property_identifier,
    },
    {
        key: "address",
        headerName: "Osoite",
        transform: (obj: IAnnotatedBuilding) => obj.address.street_address,
    },
    {
        key: "building_identifier",
        headerName: "Rakennustunnus",
    },
    {
        key: "buildings",
        headerName: "Asuntoja",
        transform: (obj: IAnnotatedBuilding) => <div className="text-right">{obj.apartment_count} kpl</div>,
    },
    {
        key: "edit",
        headerName: "",
        transform: (obj: IAnnotatedBuilding) => (
            <div className="text-right">
                <ModifyBuildingButton building={obj} />
            </div>
        ),
    },
    {
        key: "delete",
        headerName: "",
        transform: (obj: IAnnotatedBuilding) => (
            <div className="text-right">
                <DeleteBuildingButton building={obj} />
            </div>
        ),
    },
];

const LoadedHousingCompanyBuildingsPage = (): React.JSX.Element => {
    const {housingCompany} = useContext(HousingCompanyViewContext);
    if (!housingCompany) throw new Error("Housing company not found");

    // const buildingsList = housingCompany.real_estates.flatMap((obj) => obj.buildings);
    const buildingsList = housingCompany.real_estates.flatMap((realEstate) =>
        realEstate.buildings.map((building) => {
            return {
                ...building,
                real_estate: {...realEstate, buildings: undefined},
            };
        })
    );

    return (
        <>
            <Heading type="list">Rakennukset</Heading>

            <div className="buildings-table">
                {buildingsList.length ? (
                    <Table
                        cols={buildingTableColumns}
                        rows={buildingsList}
                        indexKey="id"
                        variant="light"
                        theme={tableTheme}
                        renderIndexCol={false}
                        zebra
                    />
                ) : (
                    <div>Ei rakennuksia</div>
                )}
            </div>

            <div className="row row--buttons">
                <NavigateBackButton />
                <ModifyBuildingButton />
            </div>
        </>
    );
};

const HousingCompanyBuildingsPage = (): React.JSX.Element => {
    return (
        <HousingCompanyViewContextProvider viewClassName="view--create view--buildings">
            <LoadedHousingCompanyBuildingsPage />
        </HousingCompanyViewContextProvider>
    );
};

export default HousingCompanyBuildingsPage;
