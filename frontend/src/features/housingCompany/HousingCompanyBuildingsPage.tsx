import React, {useState} from "react";

import {Fieldset, IconCrossCircle} from "hds-react";
import {useParams} from "react-router-dom";
import {useImmer} from "use-immer";

import {
    useCreateBuildingMutation,
    useGetHousingCompanyDetailQuery,
    useRemoveBuildingMutation,
} from "../../app/services";
import {
    ConfirmDialogModal,
    FormInputField,
    NavigateBackButton,
    SaveButton,
    SaveDialogModal,
} from "../../common/components";
import {IBuildingWritable} from "../../common/schemas";
import {hitasToast} from "../../common/utils";

const blankForm: IBuildingWritable = {
    real_estate_id: null,
    address: {
        street_address: "",
    },
    building_identifier: "",
};

const HousingCompanyBuildingsPage = (): JSX.Element => {
    const params = useParams() as {readonly housingCompanyId: string};
    const [isConfirmModalVisible, setIsConfirmModalVisible] = useState(false);
    const [idsToRemove, setIdsToRemove] = useState<{building?: string | null; realEstate?: string | null}>({
        building: null,
        realEstate: null,
    });
    const [isEndModalVisible, setIsEndModalVisible] = useState(false);
    const [formData, setFormData] = useImmer<IBuildingWritable>(blankForm);
    const {data: housingCompanyData, isLoading: isHousingCompanyLoading} = useGetHousingCompanyDetailQuery(
        params.housingCompanyId
    );
    const [saveBuilding, {data, error, isLoading}] = useCreateBuildingMutation();
    const [removeBuilding, {data: removeData, error: removeError, isLoading: isRemoving}] = useRemoveBuildingMutation();

    const realEstateOptions =
        isHousingCompanyLoading || !housingCompanyData
            ? []
            : housingCompanyData.real_estates.map((realEstate) => {
                  return {
                      label: `${realEstate.address.street_address} (${realEstate.property_identifier})`,
                      value: realEstate.id,
                  };
              });

    const handleSaveButtonClicked = () => {
        saveBuilding({
            data: formData,
            housingCompanyId: params.housingCompanyId as string,
            realEstateId: formData.real_estate_id as string,
        });
        setIsEndModalVisible(true);
    };

    const handleConfirmedRemove = () => {
        removeBuilding({
            id: idsToRemove.building as string,
            housingCompanyId: params.housingCompanyId as string,
            realEstateId: idsToRemove.realEstate as string,
        }).then(() => {
            hitasToast("Rakennus poistettu onnistuneesti!", "success");
            setIdsToRemove({building: null, realEstate: null});
            setIsConfirmModalVisible(false);
        });
    };

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
                                        <span className="remove-icon">
                                            <IconCrossCircle
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
            <h2>Uusi rakennus</h2>
            <div className="field-sets">
                <Fieldset heading="">
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
                <SaveButton
                    onClick={handleSaveButtonClicked}
                    isLoading={isHousingCompanyLoading}
                />
            </div>
            <SaveDialogModal
                data={data}
                error={error}
                linkURL={"/housing-companies/" + params.housingCompanyId}
                linkText="Takaisin yhtiön sivulle"
                isLoading={isLoading}
                isVisible={isEndModalVisible}
                setIsVisible={setIsEndModalVisible}
            />
            <ConfirmDialogModal
                data={removeData}
                buttonText="Poista"
                modalText="Haluatko varmasti poistaa rakennuksen?"
                successText="Rakennus poistettu"
                error={removeError}
                isLoading={isRemoving}
                isVisible={isConfirmModalVisible}
                setIsVisible={setIsConfirmModalVisible}
                confirmAction={handleConfirmedRemove}
                cancelAction={() => setIsConfirmModalVisible(false)}
            />
        </div>
    );
};

export default HousingCompanyBuildingsPage;
