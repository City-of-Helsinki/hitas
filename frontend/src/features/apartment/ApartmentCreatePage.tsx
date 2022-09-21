import React, {useState} from "react";

import {Button, Fieldset, IconCrossCircle, IconPlus, IconSaveDisketteFill, TextInput} from "hds-react";
import {useParams} from "react-router";
import {useImmer} from "use-immer";

import {
    useCreateApartmentMutation,
    useGetApartmentTypesQuery,
    useGetHousingCompanyDetailQuery,
    useGetPersonsQuery,
} from "../../app/services";
import {FormInputField, SaveDialogModal} from "../../common/components";
import {ApartmentStates, IApartmentWritable, ICode, IOwnership, IPerson} from "../../common/models";
import {dotted, formatPerson} from "../../common/utils";

const getApartmentStateLabel = (state) => {
    switch (state) {
        case "free":
            return "Vapaa";
        case "reserved":
            return "Varattu";
        case "sold":
            return "Myyty";
        default:
            return "VIRHE";
    }
};
const apartmentStateOptions = ApartmentStates.map((state) => {
    return {label: getApartmentStateLabel(state), value: state};
});

const ApartmentCreatePage = () => {
    const params = useParams();
    const {data, error, isLoading} = useGetHousingCompanyDetailQuery(params.housingCompanyId as string);
    const [createApartment, {data: savedData, error: saveError, isLoading: isSaving}] = useCreateApartmentMutation();
    const [isEndModalVisible, setIsEndModalVisible] = useState(false);

    const [formData, setFormData] = useImmer<IApartmentWritable>({
        state: "free",
        type: {id: ""},
        surface_area: 0,
        shares: {
            start: 0,
            end: 0,
        },
        address: {
            street_address: "",
            apartment_number: 0,
            floor: "",
            stair: "",
        },
        completion_date: null,
        prices: {
            debt_free_purchase_price: 0,
            purchase_price: 0,
            primary_loan_amount: 0,
            first_purchase_date: null,
            second_purchase_date: null,
            construction: {
                loans: 0,
                interest: 0,
                debt_free_purchase_price: 0,
                additional_work: 0,
            },
        },
        building: "",
        ownerships: [],
        notes: "",
    });
    const [formOwnershipsList, setFormOwnershipsList] = useImmer<IOwnership[]>([]);

    const handleSaveButtonClicked = () => {
        const formDataWithOwnerships = {
            ...formData,
            // Copy street_address from selected building
            address: {
                ...formData.address,
                street_address: buildingOptions.find((option) => option.value === formData.building)?.label || "",
            },
            // Clean away ownerships without a selected owner
            ownerships: formOwnershipsList.filter((o) => o.owner.id),
        };

        setFormData(() => formDataWithOwnerships);
        createApartment({data: formData, housingCompanyId: params.housingCompanyId as string});
        setIsEndModalVisible(true);
    };

    const handleAddOwnershipLine = () => {
        setFormOwnershipsList((draft) => {
            draft.push({
                owner: {id: ""} as IPerson,
                percentage: 100,
            });
        });
    };
    const handleSetOwnershipLine = (index, fieldPath) => (value) => {
        setFormOwnershipsList((draft) => {
            dotted(draft[index], fieldPath, value);
        });
    };
    const handleRemoveOwnershipLine = (index) => {
        setFormOwnershipsList((draft) => {
            draft.splice(index, 1);
        });
    };

    // Get all buildings that belong to HousingCompany from realestates
    const buildingOptions =
        isLoading || !data
            ? []
            : data.real_estates.flatMap((realEstate) => {
                  return realEstate.buildings.map((building) => {
                      return {label: building.address.street_address, value: building.id};
                  });
              });

    return (
        <div className="view--create view--set-apartment">
            <h1 className="main-heading">Uusi asunto</h1>
            <div className="field-sets">
                <Fieldset heading={""}>
                    <TextInput
                        id="input-housing_company.name"
                        label="Asunto-osakeyhtiö"
                        value={data?.name.display || ""}
                        disabled
                    />
                    <div className={"row"}>
                        <FormInputField
                            inputType={"select"}
                            label="Rakennus"
                            fieldPath="building"
                            options={buildingOptions || []}
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <div className={"row"}>
                        <FormInputField
                            label="Rappu"
                            fieldPath="address.stair"
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                        <FormInputField
                            inputType="number"
                            label="Asunnon numero"
                            fieldPath="address.apartment_number"
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                        <FormInputField
                            inputType="number"
                            label="Kerros"
                            fieldPath="address.floor"
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <div className={"row"}>
                        <FormInputField
                            inputType="number"
                            label="Pinta-ala"
                            fieldPath="surface_area"
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                        <FormInputField
                            inputType="relatedModel"
                            label="Asuntotyyppi"
                            fieldPath="type.id"
                            queryFunction={useGetApartmentTypesQuery}
                            relatedModelSearchField="value"
                            getRelatedModelLabel={(obj: ICode) => obj.value}
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <div className={"row"}>
                        <FormInputField
                            inputType={"select"}
                            label="Tila"
                            fieldPath="state"
                            options={apartmentStateOptions}
                            defaultValue={{label: "Vapaa", value: "free"}}
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                        <FormInputField
                            inputType="date"
                            label="Valmistumispäivä"
                            fieldPath="completion_date"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <div className="row">
                        <FormInputField
                            inputType="number"
                            label="Osakkeet, alku"
                            fieldPath="shares.start"
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                        <FormInputField
                            inputType="number"
                            label="Osakkeet, loppu"
                            fieldPath="shares.end"
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                </Fieldset>
                <Fieldset heading={""}>
                    <div className="row">
                        <FormInputField
                            inputType="number"
                            unit="€"
                            label="Velaton ostohinta"
                            fieldPath="prices.debt_free_purchase_price"
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                        <FormInputField
                            inputType="number"
                            unit="€"
                            label="Ostohinta"
                            fieldPath="prices.purchase_price"
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <div className="row">
                        <FormInputField
                            inputType="number"
                            unit="€"
                            label="Ensisijainen laina"
                            fieldPath="primary_loan_amount"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <div className="row">
                        <FormInputField
                            inputType="date"
                            label="Ensimmäinen ostopäivä"
                            fieldPath="prices.first_purchase_date"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                        <FormInputField
                            inputType="date"
                            label="Viimeinen ostopäivä"
                            fieldPath="prices.second_purchase_date"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <div className="row">
                        <FormInputField
                            inputType="number"
                            unit="€"
                            label="Rakennusaikaiset lainat"
                            fieldPath="prices.construction.loans"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                        <FormInputField
                            inputType="number"
                            unit="€"
                            label="Rakennusaikaiset korot"
                            fieldPath="prices.construction.interest"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <div className="row">
                        <FormInputField
                            inputType="number"
                            unit="€"
                            label="Rakennusaikainen velaton ostohinta"
                            fieldPath="prices.construction.debt_free_purchase_price"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                        <FormInputField
                            inputType="number"
                            unit="€"
                            label="Rakennusaikaiset lisätyöt"
                            fieldPath="prices.construction.additional_work"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                </Fieldset>
            </div>
            <div className="field-sets">
                <Fieldset heading={"Omistajuudet"}>
                    <ul className="ownerships-list">
                        <legend className={"ownership-headings"}>
                            <span>Omistaja</span>
                            <span>Omistajuusprosentti</span>
                        </legend>
                        {formOwnershipsList ? (
                            formOwnershipsList.map((ownership, index) => (
                                <li
                                    className="ownership-item"
                                    key={`ownership-item-${index}`}
                                >
                                    <div className="owner">
                                        <FormInputField
                                            inputType="relatedModel"
                                            label=""
                                            fieldPath="owner.id"
                                            queryFunction={useGetPersonsQuery}
                                            relatedModelSearchField="last_name"
                                            getRelatedModelLabel={(obj: IPerson) => formatPerson(obj)}
                                            required
                                            formData={formOwnershipsList[index]}
                                            setterFunction={handleSetOwnershipLine(index, "owner.id")}
                                            error={error}
                                        />
                                    </div>
                                    <div className="percentage">
                                        <FormInputField
                                            inputType="number"
                                            label=""
                                            fieldPath="percentage"
                                            placeholder={ownership.percentage.toString()}
                                            required
                                            formData={formOwnershipsList[index]}
                                            setterFunction={handleSetOwnershipLine(index, "percentage")}
                                            error={error}
                                        />
                                    </div>
                                    <div className="icon--remove">
                                        <IconCrossCircle
                                            size={"m"}
                                            onClick={() => handleRemoveOwnershipLine(index)}
                                        />
                                    </div>
                                </li>
                            ))
                        ) : (
                            <div>Ei omistajia</div>
                        )}
                    </ul>
                    <Button
                        onClick={handleAddOwnershipLine}
                        iconLeft={<IconPlus />}
                        variant="secondary"
                        theme="black"
                    >
                        Lisää omistajuus
                    </Button>
                </Fieldset>
                <Fieldset heading={""}>
                    <div className="row">
                        <FormInputField
                            inputType="textArea"
                            label="Muistiinpanot"
                            fieldPath="notes"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                </Fieldset>
            </div>
            <Button
                iconLeft={<IconSaveDisketteFill />}
                onClick={handleSaveButtonClicked}
                theme={"black"}
            >
                Tallenna
            </Button>

            <SaveDialogModal
                itemName={"asunnon"}
                baseURL={"/apartments/"}
                data={savedData}
                error={saveError}
                isLoading={isSaving}
                isVisible={isEndModalVisible}
                setIsVisible={setIsEndModalVisible}
            />
        </div>
    );
};

export default ApartmentCreatePage;
