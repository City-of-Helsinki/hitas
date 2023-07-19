import React, {useContext, useEffect, useState} from "react";

import {Fieldset, IconCrossCircle, IconPen} from "hds-react";
import {useImmer} from "use-immer";

import {useDeleteBuildingMutation, useSaveBuildingMutation} from "../../app/services";
import {
    ConfirmDialogModal,
    FormInputField,
    NavigateBackButton,
    SaveButton,
    SaveDialogModal,
} from "../../common/components";
import CancelButton from "../../common/components/CancelButton";
import {IBuilding, IBuildingWritable, IRealEstate} from "../../common/schemas";
import {hdsToast} from "../../common/utils";
import {
    HousingCompanyViewContext,
    HousingCompanyViewContextProvider,
} from "./components/HousingCompanyViewContextProvider";

const blankForm: IBuildingWritable = {
    real_estate_id: null,
    address: {
        street_address: "",
    },
    building_identifier: "",
};

const LoadedHousingCompanyBuildingsPage = (): React.JSX.Element => {
    const {housingCompany} = useContext(HousingCompanyViewContext);
    if (!housingCompany) throw new Error("Housing company not found");

    const [isConfirmModalVisible, setIsConfirmModalVisible] = useState(false);
    const [idsToRemove, setIdsToRemove] = useState<{building?: string | null; realEstate?: string | null}>({
        building: null,
        realEstate: null,
    });
    const [isEndModalVisible, setIsEndModalVisible] = useState(false);
    const [editing, setEditing] = useState<{building: IBuilding; realEstate: IRealEstate} | null>(null);
    const [formData, setFormData] = useImmer<IBuildingWritable>(blankForm);

    const [saveBuilding, {data, error, isLoading}] = useSaveBuildingMutation();
    const [deleteBuilding, {data: deleteData, error: deleteError, isLoading: isDeleteLoading}] =
        useDeleteBuildingMutation();

    const realEstateOptions = housingCompany.real_estates.map((realEstate) => {
        return {
            label: `${realEstate.address.street_address} (${realEstate.property_identifier})`,
            value: realEstate.id,
        };
    });

    const handleSaveBuilding = () => {
        saveBuilding({
            data: formData,
            housingCompanyId: housingCompany.id,
            realEstateId: editing ? (editing.realEstate.id as string) : (formData.real_estate_id as string),
        });
        setIsEndModalVisible(true);
    };

    const handleConfirmedRemove = () => {
        deleteBuilding({
            id: idsToRemove.building as string,
            housingCompanyId: housingCompany.id,
            realEstateId: idsToRemove.realEstate as string,
        }).then(() => {
            hdsToast.info("Rakennus poistettu onnistuneesti!");
            setIdsToRemove({building: null, realEstate: null});
            setIsConfirmModalVisible(false);
        });
    };

    const cancelEditing = () => {
        setFormData(blankForm);
        setEditing(null);
    };

    useEffect(() => {
        if (!isEndModalVisible && !error) {
            setFormData(blankForm);
            setEditing(null);
        }
    }, [isEndModalVisible, error, setFormData]);

    return (
        <div className="view--create view--buildings">
            <h1 className="main-heading">
                <span>Rakennukset</span>
            </h1>
            {housingCompany.real_estates.map((realEstate, idx) =>
                realEstate.buildings.length ? (
                    <div
                        className="buildings-list"
                        key={idx}
                    >
                        <h3>
                            Kiinteistö: {realEstate.address.street_address} ({realEstate.property_identifier})
                        </h3>
                        <ul className="detail-list__list">
                            {realEstate.buildings.map((building) => (
                                <li
                                    key={building.id}
                                    className="detail-list__list-item"
                                >
                                    {building.address.street_address}
                                    {building.building_identifier ? ` (${building.building_identifier})` : ""}
                                    <span>
                                        <IconPen
                                            className="edit-icon"
                                            onClick={() => {
                                                setEditing({building, realEstate});
                                                setFormData({
                                                    address: {street_address: building.address.street_address},
                                                    building_identifier: building.building_identifier,
                                                    real_estate_id: realEstate.id,
                                                    id: building.id,
                                                });
                                            }}
                                        />
                                        <IconCrossCircle
                                            className="remove-icon"
                                            onClick={() => {
                                                if (building.apartment_count === 0) {
                                                    setIdsToRemove({
                                                        building: building.id,
                                                        realEstate: realEstate.id,
                                                    });
                                                    setIsConfirmModalVisible(true);
                                                } else hdsToast.error("Rakennus ei ole tyhjä!");
                                            }}
                                        />
                                    </span>
                                </li>
                            ))}
                        </ul>
                    </div>
                ) : (
                    ""
                )
            )}
            <h2>{editing ? "Muokkaa rakennuksen tietoja" : "Uusi rakennus"}</h2>
            <div className="field-sets">
                <Fieldset heading="">
                    {editing && (
                        <h3>
                            Rakennus: {editing.building.address.street_address}
                            {editing.building.building_identifier ? ` (${editing.building.building_identifier})` : ""}
                        </h3>
                    )}
                    {!editing && (
                        <div className="row">
                            <FormInputField
                                inputType="select"
                                label="Kiinteistö"
                                fieldPath="real_estate_id"
                                options={realEstateOptions}
                                required
                                formData={formData}
                                setFormData={setFormData}
                                error={error}
                            />
                        </div>
                    )}
                    {editing && (
                        <div className="row">
                            <FormInputField
                                inputType="select"
                                label="Kiinteistö"
                                fieldPath="real_estate_id"
                                options={realEstateOptions}
                                defaultValue={{
                                    label: `${editing.realEstate.address.street_address} (${editing.realEstate.property_identifier})`,
                                    value: editing.realEstate.id,
                                }}
                                required
                                formData={formData}
                                setFormData={setFormData}
                                error={error}
                            />
                        </div>
                    )}
                    <div className="row">
                        <FormInputField
                            label="Katuosoite"
                            fieldPath="address.street_address"
                            options={realEstateOptions}
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                        <FormInputField
                            label="Rakennustunnus"
                            fieldPath="building_identifier"
                            tooltipText='Esimerkkiarvo: "123456789A"'
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                            className="building-identifier-field"
                        />
                    </div>
                </Fieldset>
            </div>

            <div className="row row--buttons">
                <NavigateBackButton />
                <div>
                    {editing && (
                        <CancelButton
                            onClick={cancelEditing}
                            isLoading={isLoading}
                        />
                    )}
                    <SaveButton
                        onClick={handleSaveBuilding}
                        isLoading={isLoading}
                    />
                </div>
            </div>
            <SaveDialogModal
                data={data}
                error={error}
                isLoading={isLoading}
                isVisible={isEndModalVisible}
                setIsVisible={setIsEndModalVisible}
            />
            <ConfirmDialogModal
                data={deleteData}
                buttonText="Poista"
                modalText="Haluatko varmasti poistaa rakennuksen?"
                successText="Rakennus poistettu"
                error={deleteError}
                isLoading={isDeleteLoading}
                isVisible={isConfirmModalVisible}
                setIsVisible={setIsConfirmModalVisible}
                confirmAction={handleConfirmedRemove}
                cancelAction={() => setIsConfirmModalVisible(false)}
            />
        </div>
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
