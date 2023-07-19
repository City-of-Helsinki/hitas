import React, {useContext, useRef, useState} from "react";

import {Button, IconPlus, IconTrash, Table} from "hds-react";

import {zodResolver} from "@hookform/resolvers/zod";
import {useForm} from "react-hook-form";
import {useCreateRealEstateMutation, useDeleteRealEstateMutation} from "../../app/services";
import {DeleteButton, GenericActionModal, Heading, NavigateBackButton} from "../../common/components";
import {FormProviderForm, SaveFormButton, TextInput} from "../../common/components/forms";
import {IRealEstate, WritableRealEstateSchema} from "../../common/schemas";
import {hdsToast, setAPIErrorsForFormFields} from "../../common/utils";
import {
    HousingCompanyViewContext,
    HousingCompanyViewContextProvider,
} from "./components/HousingCompanyViewContextProvider";

const tableTheme = {
    "--header-background-color": "var(--color-engel-medium-light)",
};

const CreateRealEstateButton = () => {
    const {housingCompany} = useContext(HousingCompanyViewContext);
    if (!housingCompany) throw new Error("Housing company not found");

    const [isModalOpen, setIsModalOpen] = useState(false);
    const closeModal = () => setIsModalOpen(false);

    const initialFormValues = {
        property_identifier: null,
    };
    const formRef = useRef<HTMLFormElement>(null);
    const formObject = useForm({
        defaultValues: initialFormValues,
        mode: "all",
        resolver: zodResolver(WritableRealEstateSchema),
    });

    const [saveRealEstate, {isLoading}] = useCreateRealEstateMutation();

    const onSubmit = (data) => {
        saveRealEstate({housingCompanyId: housingCompany.id, data: data})
            .unwrap()
            .then(() => {
                hdsToast.info("Kiinteistö luotu onnistuneesti.");
                closeModal();
                formObject.reset();
            })
            .catch((error) => {
                hdsToast.error("Kiinteistön luonti epäonnistui!");
                setAPIErrorsForFormFields(formObject, error);
            });
    };

    return (
        <>
            <Button
                theme="black"
                iconLeft={<IconPlus />}
                onClick={() => setIsModalOpen(true)}
            >
                Lisää uusi
            </Button>

            <GenericActionModal
                title="Uusi kiinteistö"
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
                    <TextInput
                        label="Kiinteistötunnus"
                        name="property_identifier"
                        tooltipText="Esimerkkiarvo: '1234-5678-9012-3456'"
                        required
                    />
                </FormProviderForm>
            </GenericActionModal>
        </>
    );
};

const DeleteRealEstateButton = ({realEstate}: {realEstate: IRealEstate}) => {
    const {housingCompany} = useContext(HousingCompanyViewContext);
    if (!housingCompany) throw new Error("Housing company not found");

    const [isModalOpen, setIsModalOpen] = useState(false);
    const closeModal = () => setIsModalOpen(false);

    const [deleteRealEstate, {isLoading}] = useDeleteRealEstateMutation();

    const handleDeleteRealEstate = () => {
        deleteRealEstate({housingCompanyId: housingCompany.id, id: realEstate.id})
            .unwrap()
            .then(() => {
                hdsToast.info("Kiinteistö poistettu onnistuneesti!");
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
                title="Poista kiinteistö"
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
                <p>Haluatko varmasti poistaa kiinteistön '{realEstate.property_identifier}'?</p>
            </GenericActionModal>
        </>
    );
};

const realEstateTableColumns = [
    {key: "id", headerName: "Not rendered"},
    {
        key: "address",
        headerName: "Osoite",
        transform: (obj: IRealEstate) => obj.address.street_address,
    },
    {
        key: "property_identifier",
        headerName: "Kiinteistötunnus",
    },
    {
        key: "buildings",
        headerName: "Rakennuksia",
        transform: (obj: IRealEstate) => <div className="text-right">{obj.buildings.length} kpl</div>,
    },
    {
        key: "delete",
        headerName: "",
        transform: (obj: IRealEstate) => (
            <div className="text-right">{!obj.buildings.length ? <DeleteRealEstateButton realEstate={obj} /> : ""}</div>
        ),
    },
];

const LoadedHousingCompanyRealEstatesPage = (): React.JSX.Element => {
    const {housingCompany} = useContext(HousingCompanyViewContext);
    if (!housingCompany) throw new Error("Housing company not found");

    return (
        <>
            <Heading type="list">Kiinteistöt</Heading>

            <div className="real-estates-table">
                {housingCompany.real_estates.length ? (
                    <Table
                        cols={realEstateTableColumns}
                        rows={housingCompany.real_estates}
                        indexKey="id"
                        variant="light"
                        theme={tableTheme}
                        renderIndexCol={false}
                        zebra
                    />
                ) : (
                    <div>Ei kiinteistöjä</div>
                )}
            </div>
            <div className="row row--buttons">
                <NavigateBackButton />
                <CreateRealEstateButton />
            </div>
        </>
    );
};

const HousingCompanyRealEstatesPage = (): React.JSX.Element => {
    return (
        <HousingCompanyViewContextProvider viewClassName="view--create view--real-estates">
            <LoadedHousingCompanyRealEstatesPage />
        </HousingCompanyViewContextProvider>
    );
};

export default HousingCompanyRealEstatesPage;
