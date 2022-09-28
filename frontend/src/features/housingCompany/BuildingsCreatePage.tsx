import React, {useState} from "react";

import {Button, Fieldset, IconSaveDisketteFill} from "hds-react";
import {useParams} from "react-router";
import {useNavigate} from "react-router-dom";
import {useImmer} from "use-immer";

import {useCreateBuildingMutation, useGetHousingCompanyDetailQuery} from "../../app/services";
import {FormInputField, SaveDialogModal} from "../../common/components";
import {IBuildingWritable} from "../../common/models";

const BuildingsCreatePage = (): JSX.Element => {
    const navigate = useNavigate();
    const params = useParams();
    const {data, error, isLoading} = useGetHousingCompanyDetailQuery(params.housingCompanyId as string);
    const [isEndModalVisible, setIsEndModalVisible] = useState(false);
    const blankForm = {
        address: {
            street_address: "",
        },
        building_identifier: "",
    };
    const [formData, setFormData] = useImmer<IBuildingWritable>(blankForm as IBuildingWritable);
    const [createBuilding, {data: saveData, error: saveError, isLoading: isSaving}] = useCreateBuildingMutation();

    const handleSaveButtonClicked = () => {
        createBuilding({
            data: formData,
            housingCompanyId: params.housingCompanyId as string,
            realEstateId: formData.real_estate_id as string,
        });
        setIsEndModalVisible(true);
    };
    const realEstateOptions =
        isLoading || !data
            ? []
            : data.real_estates.map((realEstate) => {
                  return {
                      label: `${realEstate.address.street_address} (${realEstate.property_identifier})`,
                      value: realEstate.id,
                  };
              });
    return (
        <div className="view--create view--create-company">
            <h1 className="main-heading">
                <span>Uusi rakennus</span>
            </h1>
            <div className="field-sets">
                <Fieldset heading="">
                    <div className="row">
                        <FormInputField
                            inputType={"select"}
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
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                            className="building-identifier-field"
                        />
                    </div>
                </Fieldset>
            </div>
            <div className="buttons">
                <Button
                    onClick={() => navigate(-1)}
                    theme={"black"}
                    className={"back-button"}
                >
                    Takaisin
                </Button>
                <Button
                    iconLeft={<IconSaveDisketteFill />}
                    onClick={handleSaveButtonClicked}
                    theme={"black"}
                >
                    Tallenna
                </Button>
            </div>
            <SaveDialogModal
                data={saveData}
                error={saveError}
                itemName="Rakennuksen"
                linkURL={"/housing-companies/" + params.housingCompanyId}
                linkText="Takaisin yhtiön sivulle"
                isLoading={isSaving}
                isVisible={isEndModalVisible}
                setIsVisible={setIsEndModalVisible}
            />
        </div>
    );
};

export default BuildingsCreatePage;
