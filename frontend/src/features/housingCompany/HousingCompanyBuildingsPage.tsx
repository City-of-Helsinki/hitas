import React, {useEffect, useState} from "react";

import {Fieldset, IconCrossCircle, IconPen} from "hds-react";
import {useParams} from "react-router-dom";
import {useImmer} from "use-immer";

import {useDeleteBuildingMutation, useGetHousingCompanyDetailQuery, useSaveBuildingMutation} from "../../app/services";
import {
    ConfirmDialogModal,
    FormInputField,
    NavigateBackButton,
    SaveButton,
    SaveDialogModal,
} from "../../common/components";
import CancelButton from "../../common/components/CancelButton";
import {IBuilding, IBuildingWritable, IRealEstate} from "../../common/schemas";
import {hitasToast} from "../../common/utils";

const blankForm: IBuildingWritable = {
    real_estate_id: null,
    address: {
        street_address: "",
    },
    building_identifier: "",
};

const HousingCompanyBuildingsPage = (): React.JSX.Element => {
    const params = useParams() as {readonly housingCompanyId: string};
    const [isConfirmModalVisible, setIsConfirmModalVisible] = useState(false);
    const [idsToRemove, setIdsToRemove] = useState<{building?: string | null; realEstate?: string | null}>({
        building: null,
        realEstate: null,
    });
    const [isEndModalVisible, setIsEndModalVisible] = useState(false);
    const [editing, setEditing] = useState<{building: IBuilding; realEstate: IRealEstate} | null>(null);
    const [formData, setFormData] = useImmer<IBuildingWritable>(blankForm);
    const {data: housingCompanyData, isLoading: isHousingCompanyLoading} = useGetHousingCompanyDetailQuery(
        params.housingCompanyId
    );
    const [saveBuilding, {data, error, isLoading}] = useSaveBuildingMutation();
    const [deleteBuilding, {data: deleteData, error: deleteError, isLoading: isDeleteLoading}] =
        useDeleteBuildingMutation();

    const realEstateOptions =
        isHousingCompanyLoading || !housingCompanyData
            ? []
            : housingCompanyData.real_estates.map((realEstate) => {
                  return {
                      label: `${realEstate.address.street_address} (${realEstate.property_identifier})`,
                      value: realEstate.id,
                  };
              });

    const handleSaveBuilding = () => {
        saveBuilding({
            data: formData,
            housingCompanyId: params.housingCompanyId as string,
            realEstateId: editing ? (editing.realEstate.id as string) : (formData.real_estate_id as string),
        });
        setIsEndModalVisible(true);
    };

    const handleConfirmedRemove = () => {
        deleteBuilding({
            id: idsToRemove.building as string,
            housingCompanyId: params.housingCompanyId as string,
            realEstateId: idsToRemove.realEstate as string,
        }).then(() => {
            hitasToast("Rakennus poistettu onnistuneesti!", "success");
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
            {housingCompanyData &&
                housingCompanyData.real_estates.map((realEstate, idx) =>
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
                                                    } else hitasToast("Rakennus ei ole tyhjä!", "error");
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
                        isLoading={isHousingCompanyLoading}
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

export default HousingCompanyBuildingsPage;
