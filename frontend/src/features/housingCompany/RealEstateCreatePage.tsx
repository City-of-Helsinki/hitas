import React, {useState} from "react";

import {Fieldset} from "hds-react";
import {useParams} from "react-router-dom";
import {useImmer} from "use-immer";

import {useCreateRealEstateMutation} from "../../app/services";
import {FormInputField, Heading, NavigateBackButton, SaveButton, SaveDialogModal} from "../../common/components";
import {IRealEstate} from "../../common/models";

const RealEstateCreatePage = (): JSX.Element => {
    const [isEndModalVisible, setIsEndModalVisible] = useState(false);
    const blankForm = {
        address: {
            street_address: "",
        },
        property_identifier: "",
    };
    const [formData, setFormData] = useImmer<IRealEstate>(blankForm as IRealEstate);
    const [saveRealEstate, {data, error, isLoading}] = useCreateRealEstateMutation();
    const params = useParams();
    const handleSaveButtonClicked = () => {
        saveRealEstate({data: formData, housingCompanyId: params.housingCompanyId as string});
        setIsEndModalVisible(true);
    };

    return (
        <div className="view--create view--create-real-estate">
            <Heading>
                <span>Uusi kiinteistö</span>
            </Heading>
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
        </div>
    );
};

export default RealEstateCreatePage;
