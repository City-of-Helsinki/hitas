import React, {useEffect, useState} from "react";

import {Button, Fieldset, IconAlertCircleFill, IconCrossCircle, IconPlus, TextInput} from "hds-react";
import {useLocation, useNavigate, useParams} from "react-router-dom";
import {useImmer} from "use-immer";
import {v4 as uuidv4} from "uuid";

import {
    useGetApartmentTypesQuery,
    useGetHousingCompanyDetailQuery,
    useGetOwnersQuery,
    useRemoveApartmentMutation,
    useSaveApartmentMutation,
} from "../../app/services";
import {
    ConfirmDialogModal,
    FormInputField,
    NavigateBackButton,
    RemoveButton,
    SaveButton,
    SaveDialogModal,
} from "../../common/components";
import {ApartmentStates, IApartmentDetails, IApartmentWritable, ICode, IOwner, IOwnership} from "../../common/models";
import {dotted, formatOwner, hitasToast} from "../../common/utils";

interface IApartmentState {
    pathname: string;
    state: null | {apartment: IApartmentDetails};
}

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

const convertApartmentDetailToWritable = (ap: IApartmentDetails): IApartmentWritable => {
    return {
        ...ap,
        shares: ap.shares || {start: null, end: null},
        ownerships: [], // Stored in a separate state, not needed here
        building: {id: ap.links.building.id},
        address: {
            ...ap.address,
            street_address: ap.links.building.street_address,
        },
    };
};

const ApartmentCreatePage = () => {
    const navigate = useNavigate();

    const {pathname, state}: IApartmentState = useLocation();
    const isEditPage = pathname.split("/").at(-1) === "edit";

    const params = useParams() as {readonly housingCompanyId: string};

    const {data: housingCompanyData, isLoading: isHousingCompanyLoading} = useGetHousingCompanyDetailQuery(
        params.housingCompanyId
    );
    const [saveApartment, {data, error, isLoading}] = useSaveApartmentMutation();
    const [removeApartment, {data: removeData, error: removeError, isLoading: isRemoving}] =
        useRemoveApartmentMutation();
    const [isEndModalVisible, setIsEndModalVisible] = useState(false);
    const [isRemoveModalVisible, setIsRemoveModalVisible] = useState(false);
    // Get all buildings that belong to HousingCompany from RealEstates
    const buildingOptions =
        isHousingCompanyLoading || !housingCompanyData
            ? []
            : housingCompanyData.real_estates.flatMap((realEstate) => {
                  return realEstate.buildings.map((building) => {
                      return {label: building.address.street_address, value: building.id};
                  });
              });
    const initialFormData: IApartmentWritable =
        state === null || state?.apartment === undefined
            ? {
                  state: "free",
                  type: {id: ""},
                  surface_area: null,
                  rooms: null,
                  shares: {
                      start: null,
                      end: null,
                  },
                  address: {
                      street_address: (buildingOptions.length === 1 && buildingOptions[0].label) || "",
                      apartment_number: null,
                      floor: null,
                      stair: null,
                  },
                  completion_date: null,
                  prices: {
                      debt_free_purchase_price: null,
                      purchase_price: null,
                      primary_loan_amount: null,
                      first_purchase_date: null,
                      latest_purchase_date: null,
                      construction: {
                          loans: null,
                          interest: null,
                          debt_free_purchase_price: null,
                          additional_work: null,
                      },
                  },
                  building: {id: (buildingOptions.length === 1 && buildingOptions[0].value) || ""},
                  ownerships: [],
                  improvements: {
                      market_price_index: [],
                      construction_price_index: [],
                  },
                  notes: "",
              }
            : convertApartmentDetailToWritable(state.apartment);
    const [formData, setFormData] = useImmer<IApartmentWritable>(initialFormData);
    const [formOwnershipsList, setFormOwnershipsList] = useImmer<(IOwnership & {key: string})[]>(
        state?.apartment !== undefined ? state.apartment.ownerships.map((o) => ({...o, key: uuidv4()})) : []
    );

    const handleSaveButtonClicked = () => {
        const formDataWithOwnerships = {
            ...formData,
            // Copy street_address from selected building
            address: {
                ...formData.address,
                street_address: buildingOptions.find((option) => option.value === formData.building.id)?.label || "",
            },

            // Clean away ownership items that don't have an owner selected
            ownerships: formOwnershipsList.filter((o) => o.owner.id),

            // Clean share fields
            shares: {
                start: formData.shares.start || null,
                end: formData.shares.end || null,
            },
        };

        setFormData(() => formDataWithOwnerships);
        saveApartment({
            data: formDataWithOwnerships,
            id: state?.apartment.id,
            housingCompanyId: params.housingCompanyId,
        });

        if (!isEditPage) {
            setIsEndModalVisible(true);
        }
    };

    const handleConfirmedRemove = () => {
        removeApartment({
            id: state?.apartment.id,
            housingCompanyId: params.housingCompanyId,
        });
    };

    // Ownerships
    const handleAddOwnershipLine = () => {
        setFormOwnershipsList((draft) => {
            draft.push({
                key: uuidv4(),
                owner: {id: ""} as IOwner,
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
    const getOwnershipPercentageError = (error) => {
        if (error && error?.data?.fields && error.data.fields.filter((e) => e.field === "ownerships.percentage")) {
            return error.data.fields.filter((e) => e.field === "ownerships.percentage")[0].message;
        }
        return "";
    };

    // Handle remove flow
    useEffect(() => {
        if (isEditPage) {
            if (!isRemoving && !removeError && removeData === null) {
                hitasToast("Asunto poistettu onnistuneesti!");
                navigate(`/housing-companies/${params.housingCompanyId}`);
            } else if (removeError) {
                setIsRemoveModalVisible(true);
            }
        }
    }, [isRemoving, removeError, removeData, navigate, isEditPage, params.housingCompanyId]);

    // Handle saving flow when editing
    useEffect(() => {
        if (isEditPage) {
            if (!isLoading && !error && data && data.id) {
                hitasToast("Asunto tallennettu onnistuneesti!");
                navigate(`/housing-companies/${data.links.housing_company.id}/apartments/${data.id}`);
            } else if (error) {
                setIsEndModalVisible(true);
            }
        }
    }, [isLoading, error, data, navigate, isEditPage]);

    // Redirect user to detail page if state is missing Apartment data and user is trying to edit the apartment
    useEffect(() => {
        if (isEditPage && state === null) navigate("..");
    }, [isEditPage, navigate, pathname, state]);

    return (
        <div className="view--create view--set-apartment">
            <h1 className="main-heading">
                {state?.apartment
                    ? `${state.apartment.address.street_address} - ${state.apartment.address.stair}
                    ${state.apartment.address.apartment_number}`
                    : "Uusi asunto"}
            </h1>
            <div className="field-sets">
                <Fieldset heading="">
                    <TextInput
                        id="input-housing_company.name"
                        label="Asunto-osakeyhtiö"
                        value={
                            housingCompanyData?.name.display !== undefined
                                ? housingCompanyData?.name.display
                                : state?.apartment !== undefined
                                ? state.apartment.links.housing_company.display_name
                                : ""
                        }
                        disabled
                    />
                    <div className="row">
                        <FormInputField
                            inputType="select"
                            label="Rakennus"
                            fieldPath="building"
                            placeholder={formData.address.street_address}
                            defaultValue={{
                                label: formData.address.street_address || "",
                                value: formData.building.id || "",
                            }}
                            options={buildingOptions || []}
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <div className="row">
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
                    </div>
                    <div className="row">
                        <FormInputField
                            inputType="number"
                            label="Kerros"
                            fieldPath="address.floor"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                        <FormInputField
                            inputType="number"
                            fractionDigits={2}
                            label="Pinta-ala"
                            fieldPath="surface_area"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <div className="row">
                        <FormInputField
                            inputType="number"
                            label="Huoneiden määrä"
                            fieldPath="rooms"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                        <FormInputField
                            inputType="relatedModel"
                            label="Asuntotyyppi"
                            fieldPath="type.id"
                            placeholder={state?.apartment !== undefined ? state.apartment.type.value : ""}
                            queryFunction={useGetApartmentTypesQuery}
                            relatedModelSearchField="value"
                            getRelatedModelLabel={(obj: ICode) => obj.value}
                            required
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <div className="row">
                        <FormInputField
                            inputType="select"
                            label="Tila"
                            fieldPath="state"
                            options={apartmentStateOptions}
                            defaultValue={{label: "Vapaa", value: "free"}}
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
                <Fieldset heading="">
                    <div className="row">
                        <FormInputField
                            inputType="number"
                            label="Osakkeet, alku"
                            fieldPath="shares.start"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                        <FormInputField
                            inputType="number"
                            label="Osakkeet, loppu"
                            fieldPath="shares.end"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                    <div className="row">
                        <FormInputField
                            inputType="number"
                            unit="€"
                            label="Luovutushinta"
                            fieldPath="prices.debt_free_purchase_price"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                        <FormInputField
                            inputType="number"
                            unit="€"
                            fractionDigits={2}
                            label="Kauppakirjahinta"
                            fieldPath="prices.purchase_price"
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
                            label="Luovutushinta (RA)"
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
                    <div className="row">
                        <FormInputField
                            inputType="number"
                            unit="€"
                            label="Ensisijaislaina"
                            fieldPath="prices.primary_loan_amount"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                        <div />
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
                            label="Viimeisin ostopäivä"
                            fieldPath="prices.latest_purchase_date"
                            formData={formData}
                            setFormData={setFormData}
                            error={error}
                        />
                    </div>
                </Fieldset>
            </div>
            <div className="field-sets">
                <Fieldset heading="Omistajuudet">
                    <ul className="ownerships-list">
                        <li>
                            <legend className="ownership-headings">
                                <span>Omistaja</span>
                                <span>Omistajuusprosentti</span>
                            </legend>
                        </li>
                        {formOwnershipsList.length ? (
                            formOwnershipsList.map((ownership: IOwnership & {key: string}, index) => (
                                <li
                                    className="ownership-item"
                                    key={`ownership-item-${ownership.key}`}
                                >
                                    <div className="owner">
                                        <FormInputField
                                            inputType="ownership"
                                            label=""
                                            fieldPath="owner.id"
                                            placeholder={ownership?.owner.name || ""}
                                            queryFunction={useGetOwnersQuery}
                                            relatedModelSearchField="name"
                                            getRelatedModelLabel={(obj: IOwner) => formatOwner(obj)}
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
                                            fractionDigits={2}
                                            placeholder={ownership.percentage.toString()}
                                            formData={formOwnershipsList[index]}
                                            setterFunction={handleSetOwnershipLine(index, "percentage")}
                                            error={error}
                                        />
                                    </div>
                                    <div className="icon--remove">
                                        <IconCrossCircle
                                            size="m"
                                            onClick={() => handleRemoveOwnershipLine(index)}
                                        />
                                    </div>
                                </li>
                            ))
                        ) : (
                            <div>Ei omistajuuksia</div>
                        )}
                        {getOwnershipPercentageError(error) && (
                            <>
                                <IconAlertCircleFill className="error-text" />
                                <span className="error-text">{getOwnershipPercentageError(error)}</span>
                            </>
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
                <Fieldset heading="">
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
            <div className="row row--buttons">
                <NavigateBackButton />
                {isEditPage && (
                    <RemoveButton
                        onClick={() => setIsRemoveModalVisible(true)}
                        isLoading={isRemoving}
                    />
                )}
                <SaveButton
                    onClick={handleSaveButtonClicked}
                    isLoading={isLoading}
                />
            </div>
            <ConfirmDialogModal
                linkText="Palaa asuntoyhtiön sivulle"
                linkURL={`/housing-companies/${params.housingCompanyId}`}
                modalText="Haluatko varmasti poistaa asunnon?"
                successText="Asunto poistettu"
                buttonText="Poista"
                isVisible={isRemoveModalVisible}
                setIsVisible={setIsRemoveModalVisible}
                data={removeData}
                error={removeError}
                isLoading={isRemoving}
                confirmAction={handleConfirmedRemove}
                cancelAction={() => setIsRemoveModalVisible(false)}
            />
            <SaveDialogModal
                linkText="Asunnon sivulle"
                baseURL={`/housing-companies/${params.housingCompanyId}/apartments/`}
                isVisible={isEndModalVisible}
                setIsVisible={setIsEndModalVisible}
                data={data}
                error={error}
                isLoading={isLoading}
            />
        </div>
    );
};

export default ApartmentCreatePage;
