import React, {useState} from "react";

import {Button, Fieldset, IconCrossCircle, IconPlus, IconSaveDisketteFill} from "hds-react";
import {useParams} from "react-router";
import {useImmer} from "use-immer";

import {
    useCreateApartmentMutation,
    useGetApartmentTypesQuery,
    useGetHousingCompaniesQuery,
    useGetHousingCompanyDetailQuery,
    useGetPersonsQuery,
} from "../../app/services";
import {FormInputField, QueryStateHandler, SaveDialogModal} from "../../common/components";
import {
    ApartmentStates,
    IApartmentWritable,
    ICode,
    IHousingCompany,
    IHousingCompanyDetails,
    IOwnership,
    IPerson,
} from "../../common/models";
import {formatPerson} from "../../common/utils";

const ApartmentCreatePage = () => {
    const params = useParams();
    const {data, error, isLoading} = useGetHousingCompanyDetailQuery(params.housingCompanyId as string);
    const [createApartment, {data: savedData, error: saveError, isLoading: isSaving}] = useCreateApartmentMutation();
    const [isEndModalVisible, setIsEndModalVisible] = useState(false);
    const blankOwnership = {
        owner: {id: ""} as IPerson,
        percentage: 100,
    };
    const blankForm: IApartmentWritable = {
        state: "free",
        apartment_type: {id: ""},
        surface_area: 0,
        share_number_start: 0,
        share_number_end: 0,
        address: {
            street_address: "",
            postal_code: "",
            apartment_number: 0,
            floor: "",
            stair: "",
        },
        apartment_number: 0,
        floor: 0,
        stair: "",
        completion_date: null,
        debt_free_purchase_price: 0,
        purchase_price: 0,
        acquisition_price: 0,
        primary_loan_amount: 0,
        loans_during_construction: 0,
        interest_during_construction: 0,
        building: {id: ""},
        real_estate: {id: ""},
        housing_company: {name: ""},
        ownerships: [blankOwnership],
        notes: "",
    };
    const [formData, setFormData] = useImmer<IApartmentWritable>(blankForm as IApartmentWritable);
    const [formOwnerships, setFormOwnerships] = useState(formData.ownerships);
    const handleSaveButtonClicked = () => {
        const formDataWithOwnerships = {...formData};
        formDataWithOwnerships.ownerships = formOwnerships as IOwnership[];
        setFormData(() => formDataWithOwnerships);
        createApartment(formData);
        setIsEndModalVisible(true);
    };
    const addOwnership = () => {
        setFormOwnerships((ownerships) => {
            return [...(ownerships as IOwnership[]), blankOwnership];
        });
    };
    const removeOwnership = (num) => {
        const newFormOwnerships = formData.ownerships as IOwnership[];
        newFormOwnerships.splice(num, 1);
        setFormData(({ownerships}) => newFormOwnerships);
    };
    const LoadedApartmentCreatePage = ({data}: {data: IHousingCompanyDetails}) => {
        const buildingOptions = data.real_estates.flatMap((realEstate) => {
            return realEstate.buildings.map((building) => {
                return {label: building.address.street_address};
            });
        });
        const stateName = (state) => {
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
        const stateOptions = ApartmentStates.map((state) => {
            return {label: stateName(state), value: state};
        });
        return (
            <div className="view--create view--set-apartment">
                <h1 className="main-heading">Uusi asunto</h1>
                <div className="field-sets">
                    <Fieldset heading={""}>
                        <FormInputField
                            inputType="relatedModel"
                            label="Asunto-osakeyhtiö"
                            requestedField="id"
                            fieldPath="housing_company"
                            placeholder={data.name.display}
                            queryFunction={useGetHousingCompaniesQuery}
                            relatedModelSearchField="value"
                            getRelatedModelLabel={(obj: IHousingCompany) => obj.name}
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                        <div className={"row"}>
                            <FormInputField
                                inputType={"select"}
                                label="Rakennus"
                                fieldPath="building.id"
                                options={buildingOptions}
                                required
                                formData={formData}
                                setFormData={setFormData}
                                error={error}
                            />
                        </div>
                        <div className={"row"}>
                            <FormInputField
                                label="Rappu"
                                fieldPath="stair"
                                required
                                formData={formData}
                                setFormData={setFormData}
                                error={error}
                            />
                            <FormInputField
                                inputType="number"
                                label="Asunnon numero"
                                fieldPath="apartment_number"
                                required
                                formData={formData}
                                setFormData={setFormData}
                                error={error}
                            />
                            <FormInputField
                                inputType="number"
                                label="Kerros"
                                fieldPath="floor"
                                required
                                formData={formData}
                                setFormData={setFormData}
                                error={error}
                            />
                        </div>
                        <div className="row">
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
                                requestedField="value"
                                fieldPath="apartment_type.id"
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
                                options={stateOptions}
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
                    </Fieldset>
                    <Fieldset heading={""}>
                        <div className="row">
                            <FormInputField
                                inputType="number"
                                unit="€"
                                label="Velaton ostohinta"
                                fieldPath="debt_free_purchase_price"
                                required
                                formData={formData}
                                setFormData={setFormData}
                                error={error}
                            />
                            <FormInputField
                                inputType="number"
                                unit="€"
                                label="Ostohinta"
                                fieldPath="purchase_price"
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
                                label="Hankinta-arvo"
                                fieldPath="acquisition_price"
                                required
                                formData={formData}
                                setFormData={setFormData}
                                error={error}
                            />
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
                                inputType="number"
                                label="Osakkeet, alku"
                                fieldPath="share_number_start"
                                required
                                formData={formData}
                                setFormData={setFormData}
                                error={error}
                            />
                            <FormInputField
                                inputType="number"
                                label="Osakkeet, loppu"
                                fieldPath="share_number_end"
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
                                label="Rakennusaikaiset lainat"
                                fieldPath="loans_during_construction"
                                formData={formData}
                                setFormData={setFormData}
                                error={error}
                            />
                            <FormInputField
                                inputType="number"
                                unit="€"
                                label="Rakennusaikaiset korot"
                                fieldPath="interest_during_construction"
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
                            {formOwnerships ? (
                                formOwnerships.map((ownership, num) => (
                                    <li
                                        className="ownership-item"
                                        key={num}
                                    >
                                        <div className="owner">
                                            <FormInputField
                                                inputType="relatedModel"
                                                label=""
                                                requestedField="id"
                                                fieldPath="id"
                                                queryFunction={useGetPersonsQuery}
                                                relatedModelSearchField="last_name"
                                                getRelatedModelLabel={(obj: IPerson) => formatPerson(obj)}
                                                required
                                                formData={formOwnerships}
                                                setFormData={setFormOwnerships}
                                                error={error}
                                            />
                                        </div>
                                        <div className="percentage">
                                            <FormInputField
                                                inputType="number"
                                                label=""
                                                fieldPath={`percentage`}
                                                placeholder={ownership.percentage.toString()}
                                                required
                                                formData={formOwnerships}
                                                setFormData={setFormOwnerships}
                                                error={error}
                                            />
                                        </div>
                                        {num > 0 && (
                                            <div className="icon--remove">
                                                <IconCrossCircle
                                                    size={"m"}
                                                    onClick={() => removeOwnership(num)}
                                                />
                                            </div>
                                        )}
                                    </li>
                                ))
                            ) : (
                                <div>Ei omistajia</div>
                            )}
                        </ul>
                        <Button
                            onClick={addOwnership}
                            iconLeft={<IconPlus />}
                            variant="secondary"
                            theme="black"
                        >
                            Lisää omistajuus
                        </Button>
                    </Fieldset>
                    <Fieldset heading={""}></Fieldset>
                </div>
                <Button
                    iconLeft={<IconSaveDisketteFill />}
                    onClick={handleSaveButtonClicked}
                    theme={"black"}
                >
                    Tallenna
                </Button>
                {/*
                 Save attempt modal dialog
                 */}
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
    return (
        <QueryStateHandler
            data={data}
            error={error}
            isLoading={isLoading}
        >
            <LoadedApartmentCreatePage data={data as IHousingCompanyDetails} />
        </QueryStateHandler>
    );
};

export default ApartmentCreatePage;
