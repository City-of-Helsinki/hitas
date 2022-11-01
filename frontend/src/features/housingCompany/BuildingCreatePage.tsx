import React, {useState} from "react";

import {Fieldset} from "hds-react";
import {useParams} from "react-router-dom";
import {useImmer} from "use-immer";

import {useCreateBuildingMutation, useGetHousingCompanyDetailQuery} from "../../app/services";
import {FormInputField, NavigateBackButton, SaveButton, SaveDialogModal} from "../../common/components";
import {IBuildingWritable} from "../../common/models";

const blankForm: IBuildingWritable = {
    real_estate_id: null,
    address: {
        street_address: "",
    },
    building_identifier: "",
};

const BuildingCreatePage = (): JSX.Element => {
    const params = useParams() as {readonly housingCompanyId: string};
    const [isEndModalVisible, setIsEndModalVisible] = useState(false);

    const [formData, setFormData] = useImmer<IBuildingWritable>(blankForm);
    const {data: housingCompanyData, isLoading: housingCompanyIsLoading} = useGetHousingCompanyDetailQuery(
        params.housingCompanyId
    );
    const [saveBuilding, {data, error, isLoading}] = useCreateBuildingMutation();

    const realEstateOptions =
        housingCompanyIsLoading || !housingCompanyData
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

    return (
        <div className="view--create view--create-company">
            <h1 className="main-heading">
                <span>Uusi rakennus</span>
            </h1>
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
            <div className="buttons">
                <NavigateBackButton />
                <SaveButton
                    onClick={handleSaveButtonClicked}
                    isLoading={housingCompanyIsLoading}
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
        </div>
    );
};

export default BuildingCreatePage;
