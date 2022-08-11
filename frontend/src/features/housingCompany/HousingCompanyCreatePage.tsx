import React from "react";

import {Button, Fieldset, IconSaveDisketteFill, NumberInput, TextArea, TextInput} from "hds-react";
import {useImmer} from "use-immer";

import {useCreateHousingCompanyMutation} from "../../app/services";
import {IHousingCompanyState, IHousingCompanyWritable} from "../../common/models";

const HousingCompanyCreatePage = () => {
    const [formData, setFormData] = useImmer<IHousingCompanyWritable>({
        acquisition_price: {initial: 10.0, realized: 10.0},
        address: {
            postal_code: "00100",
            street: "test-street-address-1",
        },
        building_type: {id: "f3a77a469fc34b45ba6dbaeebacd8a33"},
        business_id: "1234567-8",
        developer: {id: "06224336de274d87853afb950ba5ecc8"},
        financing_method: {id: "0a76cff05ecf4ebab050204c3477d1c9"},
        name: {
            display: "test-housing-company-1",
            official: "test-housing-company-1-as-oy",
        },
        notes: "This is a note.",
        primary_loan: 10.0,
        property_manager: {id: "2d9a7fac81e5426db3b33d6ad6ca9949"},
        state: "not_ready",
        sales_price_catalogue_confirmation_date: "2022-01-01",
    });
    const [createHousingCompany, response] = useCreateHousingCompanyMutation();
    console.log(response);

    const handleSaveButtonClicked = () => {
        createHousingCompany(formData);
    };

    return (
        <div className="company-details">
            <h1 className="main-heading">
                <span>Uusi asunto-yhtiö</span>
            </h1>
            <Fieldset
                heading="Perustiedot"
                style={{
                    display: "flex",
                    flexDirection: "column",
                    gridGap: "1em",
                }}
            >
                <TextInput
                    label="Yhtiön hakunimi"
                    id="name.display"
                    value={formData.name.display}
                    onChange={(e) =>
                        setFormData((draft) => {
                            draft.name.display = e.target.value;
                        })
                    }
                    required
                />
                <TextInput
                    label="Yhtiön virallinen nimi"
                    id="name.official"
                    value={formData.name.official}
                    onChange={(e) =>
                        setFormData((draft) => {
                            draft.name.official = e.target.value;
                        })
                    }
                    required
                />
                <TextInput
                    label="Virallinen osoite"
                    id="address.street"
                    value={formData.address.street}
                    onChange={(e) =>
                        setFormData((draft) => {
                            draft.address.street = e.target.value;
                        })
                    }
                    required
                />
                <TextInput
                    label="Postinumero"
                    id="address.postal_code"
                    value={formData.address.postal_code}
                    onChange={(e) =>
                        setFormData((draft) => {
                            draft.address.postal_code = e.target.value;
                        })
                    }
                    required
                />
                <TextInput
                    label="state"
                    id="state"
                    value={formData.state}
                    onChange={(e) =>
                        setFormData((draft) => {
                            draft.state = e.target.value as IHousingCompanyState;
                        })
                    }
                    required
                />
                <NumberInput
                    label="Hankinta-arvo"
                    id="acquisition_price.initial"
                    value={formData.acquisition_price.initial}
                    onChange={(e) =>
                        setFormData((draft) => {
                            draft.acquisition_price.initial = Number(Number(e.target.value).toFixed(2));
                        })
                    }
                    unit="€"
                    required
                />
                <NumberInput
                    label="Hankinta-arvo"
                    id="acquisition_price.realized"
                    value={formData.acquisition_price.realized || ""}
                    onChange={(e) =>
                        setFormData((draft) => {
                            draft.acquisition_price.realized = Number(Number(e.target.value).toFixed(2));
                        })
                    }
                    unit="€"
                />
            </Fieldset>
            <Fieldset
                heading="Lisätiedot"
                style={{
                    display: "flex",
                    flexDirection: "column",
                    gridGap: "1em",
                }}
            >
                <TextInput
                    label="business_id"
                    id="business_id"
                    value={formData.business_id}
                    onChange={(e) =>
                        setFormData((draft) => {
                            draft.business_id = e.target.value;
                        })
                    }
                    required
                />
                <TextInput
                    label="sales_price_catalogue_confirmation_date"
                    id="sales_price_catalogue_confirmation_date"
                    value={formData.sales_price_catalogue_confirmation_date || ""}
                    onChange={(e) =>
                        setFormData((draft) => {
                            draft.sales_price_catalogue_confirmation_date = e.target.value;
                        })
                    }
                />
                <NumberInput
                    label="primary_loan"
                    id="primary_loan"
                    value={formData.primary_loan || ""}
                    onChange={(e) =>
                        setFormData((draft) => {
                            draft.primary_loan = Number(Number(e.target.value).toFixed(2));
                        })
                    }
                    unit="€"
                />

                <TextInput
                    label="financing_method"
                    id="financing_method"
                    value={formData.financing_method.id}
                    onChange={(e) =>
                        setFormData((draft) => {
                            draft.financing_method.id = e.target.value;
                        })
                    }
                    required
                />
                <TextInput
                    label="building_type"
                    id="building_type"
                    value={formData.building_type.id}
                    onChange={(e) =>
                        setFormData((draft) => {
                            draft.building_type.id = e.target.value;
                        })
                    }
                    required
                />
                <TextInput
                    label="developer"
                    id="developer"
                    value={formData.developer.id}
                    onChange={(e) =>
                        setFormData((draft) => {
                            draft.developer.id = e.target.value;
                        })
                    }
                    required
                />
                <TextInput
                    label="property_manager"
                    id="property_manager"
                    value={formData.property_manager.id}
                    onChange={(e) =>
                        setFormData((draft) => {
                            draft.property_manager.id = e.target.value;
                        })
                    }
                    required
                />
                <TextArea
                    label="notes"
                    id="notes"
                    value={formData.notes || ""}
                    onChange={(e) =>
                        setFormData((draft) => {
                            draft.notes = e.target.value;
                        })
                    }
                />
            </Fieldset>
            <Button
                iconLeft={<IconSaveDisketteFill />}
                onClick={handleSaveButtonClicked}
            >
                Tallenna
            </Button>
        </div>
    );
};

export default HousingCompanyCreatePage;
