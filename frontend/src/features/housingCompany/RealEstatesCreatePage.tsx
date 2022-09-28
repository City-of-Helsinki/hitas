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
                <span>Uusi kiinteistö</span>
            </h1>
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
                data={data}
                error={error}
                itemName="Kiinteistön"
                linkURL={"/housing-companies/" + params.housingCompanyId}
                linkText="Takaisin yhtiön sivulle"
                isLoading={isLoading}
                isVisible={isEndModalVisible}
                setIsVisible={setIsEndModalVisible}
            />
        </div>
    );
};

export default RealEstatesCreatePage;
