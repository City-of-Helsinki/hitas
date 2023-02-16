import React, {useEffect, useRef, useState} from "react";

import {zodResolver} from "@hookform/resolvers/zod";
import {Fieldset} from "hds-react";
import {SubmitHandler, useForm} from "react-hook-form";
import {useLocation, useNavigate, useParams} from "react-router-dom";
import {useImmer} from "use-immer";
import {v4 as uuidv4} from "uuid";

import {
    useGetApartmentTypesQuery,
    useGetHousingCompanyDetailQuery,
    useRemoveApartmentMutation,
    useSaveApartmentMutation,
} from "../../app/services";
import {
    ConfirmDialogModal,
    FormInputField,
    Heading,
    NavigateBackButton,
    RemoveButton,
    SaveButton,
    SaveDialogModal,
} from "../../common/components";
import {DateInput, NumberInput, RelatedModelInput, Select, TextInput} from "../../common/components/form";
import {
    ApartmentWritableSchema,
    IApartmentDetails,
    IApartmentWritable,
    ICode,
    apartmentStates,
} from "../../common/schemas";
import {hitasToast} from "../../common/utils";
import ApartmentHeader from "./components/ApartmentHeader";

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

const apartmentStateOptions = apartmentStates.map((state) => {
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
        prices: {
            ...ap.prices,
            construction: {
                ...ap.prices.construction,
                interest: ap.prices.construction.interest || {
                    rate_6: null,
                    rate_14: null,
                },
            },
        },
    };
};

const ApartmentCreatePage = () => {
    const navigate = useNavigate();
    const {pathname, state}: IApartmentState = useLocation();
    const params = useParams() as {readonly housingCompanyId: string};
    const formRef = useRef<HTMLFormElement | null>(null);
    const {data: housingCompanyData, isLoading: isHousingCompanyLoading} = useGetHousingCompanyDetailQuery(
        params.housingCompanyId
    );
    const [saveApartment, {data, error, isLoading}] = useSaveApartmentMutation();
    const [removeApartment, {data: removeData, error: removeError, isLoading: isRemoving}] =
        useRemoveApartmentMutation();
    // Get all buildings that belong to HousingCompany from RealEstates
    const buildingOptions =
        isHousingCompanyLoading || !housingCompanyData
            ? []
            : housingCompanyData.real_estates.flatMap((realEstate) => {
                  return realEstate.buildings.map((building) => {
                      return {label: building.address.street_address, value: building.id};
                  });
              });

    // Form
    const initialFormData: IApartmentWritable =
        state === null || state?.apartment === undefined
            ? {
                  state: "free",
                  type: {id: null},
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
                      stair: "",
                  },
                  completion_date: null,
                  prices: {
                      first_sale_purchase_price: null,
                      latest_sale_purchase_price: null,
                      first_sale_share_of_housing_company_loans: null,
                      first_purchase_date: null,
                      latest_purchase_date: null,
                      construction: {
                          loans: null,
                          interest: {
                              rate_6: null,
                              rate_14: null,
                          },
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
    const formObject = useForm<IApartmentWritable>({
        defaultValues: initialFormData,
        mode: "all",
        reValidateMode: "onBlur",
        resolver: zodResolver(ApartmentWritableSchema),
    });
    const onSubmit: SubmitHandler<IApartmentWritable> = (data) => {
        const formDataWithOwnerships = {
            ...data,
            // Copy street_address from selected building
            address: {
                ...data.address,
                street_address: buildingOptions.find((option) => option.value === formData.building.id)?.label || "",
            },

            // Clean away ownership items that don't have an owner selected
            ownerships: formOwnershipsList.filter((o) => o.owner.id),

            // Clean share fields
            shares: {
                start: formObject.getValues("shares.start") ?? null,
                end: formObject.getValues("shares.end") ?? null,
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

    const [formData, setFormData] = useImmer<IApartmentWritable>(initialFormData);
    const formOwnershipsList =
        state?.apartment !== undefined ? state.apartment.ownerships.map((o) => ({...o, key: uuidv4()})) : [];

    // Flags
    const isEditPage = pathname.split("/").at(-1) === "edit";
    const [isEndModalVisible, setIsEndModalVisible] = useState(false);
    const [isRemoveModalVisible, setIsRemoveModalVisible] = useState(false);

    // Event handlers
    const handleSubmitButtonClick = () => {
        formRef.current && formRef.current.dispatchEvent(new Event("submit", {cancelable: true, bubbles: true}));
    };

    const handleConfirmedRemove = () => {
        removeApartment({
            id: state?.apartment.id,
            housingCompanyId: params.housingCompanyId,
        });
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
        <div className="view--create">
            {state?.apartment ? <ApartmentHeader apartment={state.apartment} /> : <Heading>Uusi asunto</Heading>}
            <form
                ref={formRef}
                onSubmit={formObject.handleSubmit(onSubmit, (errors) => console.warn(formObject, errors))}
            >
                <div className="field-sets">
                    <Fieldset heading="">
                        <div className="input-field">
                            <TextInput
                                name="housing_company"
                                id="input-housing_company.name"
                                label="Asunto-osakeyhtiö"
                                value={
                                    housingCompanyData?.name.display !== undefined
                                        ? housingCompanyData?.name.display
                                        : state?.apartment !== undefined
                                        ? state.apartment.links.housing_company.display_name
                                        : ""
                                }
                                formObject={formObject}
                                disabled
                            />
                        </div>
                        <div className="row">
                            <Select
                                label="Rakennus"
                                options={buildingOptions || []}
                                name="building"
                                // placeholder={formData.address.street_address}
                                defaultValue={{
                                    label: formData.address.street_address || "",
                                    value: formData.building.id || "",
                                }}
                                formObject={formObject}
                                required
                            />
                        </div>
                        <div className="row">
                            <TextInput
                                name="address.stair"
                                label="Rappu"
                                formObject={formObject}
                                required
                            />
                            <NumberInput
                                name="address.apartment_number"
                                label="Asunnon numero"
                                formObject={formObject}
                                required
                            />
                        </div>
                        <div className="row">
                            <NumberInput
                                name="address.floor"
                                label="Kerros"
                                formObject={formObject}
                            />
                            <NumberInput
                                name="address.apartment_number"
                                label="Pinta-ala"
                                formObject={formObject}
                                fractionDigits={2}
                                unit="m²"
                            />
                        </div>
                        <div className="row">
                            <NumberInput
                                name="rooms"
                                label="Huoneiden määrä"
                                formObject={formObject}
                            />
                            <RelatedModelInput
                                name="type.id"
                                label="Asuntotyyppi"
                                fieldPath="type.id"
                                placeholder={state?.apartment.type !== null ? state?.apartment.type.value : ""}
                                queryFunction={useGetApartmentTypesQuery}
                                relatedModelSearchField="value"
                                getRelatedModelLabel={(obj: ICode) => obj.value}
                                formObject={formObject}
                            />
                        </div>
                        <div className="row">
                            <Select
                                label="Tila"
                                name="state"
                                options={apartmentStateOptions}
                                defaultValue={{label: "Vapaa", value: "free"}}
                                formObject={formObject}
                            />
                            <DateInput
                                label="Valmistumispäivä"
                                name="completion_date"
                                formObject={formObject}
                            />
                        </div>
                    </Fieldset>
                    <Fieldset heading="">
                        <div className="row">
                            <NumberInput
                                name="shares.start"
                                label="Osakkeet, alku"
                                formObject={formObject}
                            />
                            <NumberInput
                                name="shares.end"
                                label="Osakkeet, loppu"
                                formObject={formObject}
                            />
                        </div>
                        <div className="row">
                            <NumberInput
                                name="prices.construction.loans"
                                label="Rakennusaikaiset lainat"
                                unit="€"
                                fractionDigits={2}
                                formObject={formObject}
                            />
                            <NumberInput
                                name="prices.construction.interest.rate_6"
                                label="Rak.aik. korko (6%)"
                                unit="€"
                                fractionDigits={2}
                                formObject={formObject}
                            />
                            <NumberInput
                                name="prices.construction.interest.rate_14"
                                label="Rak.aik. korko (14%)"
                                unit="€"
                                fractionDigits={2}
                                formObject={formObject}
                            />
                        </div>
                        <div className="row">
                            <NumberInput
                                name="prices.construction.debt_free_purchase_price"
                                label="Luovutushinta (RA)"
                                unit="€"
                                fractionDigits={2}
                                formObject={formObject}
                            />
                            <NumberInput
                                name="prices.construction.additional_work"
                                label="Rakennusaikaiset lisätyöt"
                                unit="€"
                                fractionDigits={2}
                                formObject={formObject}
                            />
                        </div>
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
            </form>
            <div className="row row--buttons">
                <NavigateBackButton />
                {isEditPage && (
                    <RemoveButton
                        onClick={() => setIsRemoveModalVisible(true)}
                        isLoading={isRemoving}
                    />
                )}
                <SaveButton
                    onClick={handleSubmitButtonClick}
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
