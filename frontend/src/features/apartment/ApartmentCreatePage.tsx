import {useEffect, useRef, useState} from "react";

import {zodResolver} from "@hookform/resolvers/zod";
import {Fieldset} from "hds-react";
import {SubmitHandler, useForm} from "react-hook-form";
import {useLocation, useNavigate, useParams} from "react-router-dom";
import {v4 as uuidv4} from "uuid";

import {
    useGetApartmentTypesQuery,
    useGetHousingCompanyDetailQuery,
    useRemoveApartmentMutation,
    useSaveApartmentMutation,
} from "../../app/services";
import {
    ConfirmDialogModal,
    Heading,
    NavigateBackButton,
    RemoveButton,
    SaveButton,
    SaveDialogModal,
} from "../../common/components";
import {
    DateInput,
    NumberInput,
    RelatedModelInput,
    Select,
    TextAreaInput,
    TextInput,
} from "../../common/components/form";
import {getApartmentStateLabel} from "../../common/localisation";
import {
    apartmentStates,
    ApartmentWritableFormSchema,
    IApartmentDetails,
    IApartmentWritable,
    IApartmentWritableForm,
    ICode,
} from "../../common/schemas";
import {hitasToast} from "../../common/utils";
import ApartmentHeader from "./components/ApartmentHeader";

interface IApartmentState {
    pathname: string;
    state: null | {apartment: IApartmentDetails};
}

const apartmentStateOptions = apartmentStates.map((state) => {
    return {label: getApartmentStateLabel(state), value: state};
});

const convertApartmentDetailToWritable = (ap: IApartmentDetails): IApartmentWritableForm => {
    return {
        ...ap,
        shares: ap.shares || {start: null, end: null},
        ownerships: [], // Stored in a separate state, not needed here
        building: {label: ap.links.building.street_address, value: ap.links.building.id},
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
    const initialFormData: IApartmentWritableForm =
        state === null || state?.apartment === undefined
            ? {
                  state: "free",
                  type: {id: null},
                  surface_area: null,
                  rooms: null,
                  shares: {start: null, end: null},
                  address: {
                      apartment_number: null,
                      floor: null,
                      stair: "",
                  },
                  completion_date: null,
                  prices: {
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
                  building:
                      buildingOptions.length === 1
                          ? {label: buildingOptions[0].label, value: buildingOptions[0].value}
                          : {label: "", value: ""},
                  ownerships: [],
                  improvements: {
                      market_price_index: [],
                      construction_price_index: [],
                  },
                  notes: "",
              }
            : convertApartmentDetailToWritable(state.apartment);
    const formObject = useForm<IApartmentWritableForm>({
        defaultValues: initialFormData,
        mode: "all",
        reValidateMode: "onBlur",
        resolver: zodResolver(ApartmentWritableFormSchema),
    });
    const onSubmit: SubmitHandler<IApartmentWritableForm> = (data) => {
        const formattedFormData: IApartmentWritable = {
            ...data,
            // Copy street_address from selected building
            address: {...data.address, street_address: data.building.label},
            building: {id: data.building.value},

            // Clean away ownership items that don't have an owner selected
            ownerships: formOwnershipsList.filter((o) => o.owner.id),

            // Clean share fields
            shares: {
                start: formObject.getValues("shares.start") ?? null,
                end: formObject.getValues("shares.end") ?? null,
            },
        };

        saveApartment({
            data: formattedFormData,
            id: state?.apartment.id,
            housingCompanyId: params.housingCompanyId,
        });

        if (!isEditPage) {
            setIsEndModalVisible(true);
        }
    };

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
                                defaultValue={{
                                    label: initialFormData.building.label || "",
                                    value: initialFormData.building.value || "",
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
                                name="surface_area"
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
                                required
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
                            <TextAreaInput
                                name="notes"
                                label="Muistiinpanot"
                                formObject={formObject}
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
