import React, {useState} from "react";

import {Fieldset, IconCrossCircle} from "hds-react";
import {useParams} from "react-router-dom";
import {useImmer} from "use-immer";

import {
    useCreateRealEstateMutation,
    useDeleteRealEstateMutation,
    useGetHousingCompanyDetailQuery,
} from "../../app/services";
import {
    ConfirmDialogModal,
    FormInputField,
    NavigateBackButton,
    SaveButton,
    SaveDialogModal,
} from "../../common/components";
import {IRealEstate} from "../../common/schemas";
import {hitasToast} from "../../common/utils";

const HousingCompanyRealEstatesPage = (): React.JSX.Element => {
    const params = useParams();
    const [isConfirmModalVisible, setIsConfirmModalVisible] = useState(false);
    const [isEndModalVisible, setIsEndModalVisible] = useState(false);
    const [realEstateToRemove, setRealEstateToRemove] = useState<string | null>();
    const {data: housingCompanyData, isLoading: isHousingCompanyLoading} = useGetHousingCompanyDetailQuery(
        params.housingCompanyId as string
    );
    const blankForm = {
        address: {
            street_address: "",
        },
        property_identifier: "",
    };
    const [formData, setFormData] = useImmer<IRealEstate>(blankForm as IRealEstate);
    const [saveRealEstate, {data, error, isLoading}] = useCreateRealEstateMutation();

    const [deleteRealEstate, {data: deleteData, error: deleteError, isLoading: isDeleteLoading}] =
        useDeleteRealEstateMutation();
    const handleSaveButtonClicked = () => {
        saveRealEstate({data: formData, housingCompanyId: params.housingCompanyId as string});
        setIsEndModalVisible(true);
    };
    const handleConfirmedRemove = () => {
        deleteRealEstate({id: realEstateToRemove as string, housingCompanyId: params.housingCompanyId as string}).then(
            () => {
                setRealEstateToRemove(null);
                setIsConfirmModalVisible(false);
                hitasToast("Kiinteistö poistettu onnistuneesti!", "success");
            }
        );
    };

    return (
        <div className="view--create view--real-estates">
            <h1 className="main-heading">
                <span>Kiinteistöt</span>
            </h1>
            <ul className="detail-list__list real-estates-list">
                {housingCompanyData &&
                    !isHousingCompanyLoading &&
                    housingCompanyData.real_estates.map((realEstate) => (
                        <li
                            className="detail-list__list-item"
                            key={realEstate.id}
                        >
                            {realEstate.address.street_address} ({realEstate.property_identifier})
                            <span className="remove-icon">
                                <IconCrossCircle
                                    onClick={() => {
                                        if (realEstate.buildings.length) {
                                            hitasToast("Kiinteistö ei ole tyhjä!", "error");
                                        } else {
                                            setRealEstateToRemove(realEstate.id);
                                            setIsConfirmModalVisible(true);
                                        }
                                    }}
                                />
                            </span>
                        </li>
                    ))}
            </ul>
            <h2>Uusi kiinteistö</h2>
            <div className="field-sets">
                <Fieldset heading="">
                    <div className="row">
                        <FormInputField
                            label="Katuosoite"
                            fieldPath="address.street_address"
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                        <FormInputField
                            label="Kiinteistötunnus"
                            fieldPath="property_identifier"
                            tooltipText={'Esimerkkiarvo: "1234-5678-9012-3456"'}
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                </Fieldset>
            </div>
            <div className="row row--buttons">
                <NavigateBackButton />
                <SaveButton
                    onClick={handleSaveButtonClicked}
                    isLoading={isLoading}
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
                data={deleteData}
                modalText="Haluatko varmasti poistaa kiinteistön?"
                successText="Kiinteistö poistettu"
                error={deleteError}
                isLoading={isDeleteLoading}
                isVisible={isConfirmModalVisible}
                setIsVisible={setIsConfirmModalVisible}
                confirmAction={handleConfirmedRemove}
                cancelAction={() => setIsConfirmModalVisible(false)}
                buttonText="Poista"
            />
        </div>
    );
};

export default HousingCompanyRealEstatesPage;
