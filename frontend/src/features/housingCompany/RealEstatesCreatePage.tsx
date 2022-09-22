import React, {useState} from "react";

import {Button, Fieldset, IconSaveDisketteFill} from "hds-react";
import {useParams} from "react-router";
import {useNavigate} from "react-router-dom";
import {useImmer} from "use-immer";

import {useCreateRealEstateMutation} from "../../app/services";
import {FormInputField, SaveDialogModal} from "../../common/components";
import {IRealEstate} from "../../common/models";

const RealEstatesCreatePage = (): JSX.Element => {
    const [isEndModalVisible, setIsEndModalVisible] = useState(false);
    const blankForm = {
        address: {
            street_address: "",
        },
        property_identifier: "",
    };
    const [formData, setFormData] = useImmer<IRealEstate>(blankForm as IRealEstate);
    const [createBuilding, {data, error, isLoading}] = useCreateRealEstateMutation();
    const navigate = useNavigate();
    const params = useParams();
    const handleSaveButtonClicked = () => {
        createBuilding({data: formData, housingCompanyId: params.housingCompanyId as string});
        setIsEndModalVisible(true);
    };

    return (
        <div className="view--create view--create-real-estate">
            <h1 className="main-heading">
                <span>Uusi rakennus</span>
            </h1>
            <div className="field-sets">
                <Fieldset heading="Rakennuksen tiedot">
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
                            tooltipText={'Esimerkkiarvo: "196-15-74-3"'}
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
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
            {/*
             Save attempt modal dialog
             */}
            <SaveDialogModal
                data={data}
                error={error}
                baseURL="/housing-companies/"
                itemName="Kiinteistön"
                isLoading={isLoading}
                isVisible={isEndModalVisible}
                setIsVisible={setIsEndModalVisible}
            />
        </div>
    );
};

export default RealEstatesCreatePage;
