import {useEffect, useRef, useState} from "react";

import {zodResolver} from "@hookform/resolvers/zod";
import {Fieldset} from "hds-react";
import {SubmitHandler, useForm} from "react-hook-form";
import {useNavigate, useParams} from "react-router-dom";
import {v4 as uuidv4} from "uuid";

import {
    useDeleteApartmentMutation,
    useGetApartmentDetailQuery,
    useGetApartmentTypesQuery,
    useGetHousingCompanyDetailQuery,
    useSaveApartmentMutation,
} from "../../app/services";
import {
    ConfirmDialogModal,
    Heading,
    NavigateBackButton,
    QueryStateHandler,
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
    IHousingCompanyDetails,
} from "../../common/schemas";
import {hitasToast} from "../../common/utils";
import ApartmentHeader from "./components/ApartmentHeader";

const apartmentStateOptions = apartmentStates.map((state) => {
    return {label: getApartmentStateLabel(state), value: state};
});

const getInitialFormData = (apartment, buildingOptions): IApartmentWritableForm => {
    if (apartment) {
        return convertApartmentDetailToWritable(apartment);
    } else {
        return {
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
        };
    }
};

const convertApartmentDetailToWritable = (apartment: IApartmentDetails): IApartmentWritableForm => {
    return {
        ...apartment,
        shares: apartment.shares || {start: null, end: null},
        building: {label: apartment.links.building.street_address, value: apartment.links.building.id},
        ownerships: [], // Stored in a separate state, not needed here
    };
};

const LoadedApartmentCreatePage = ({
    housingCompany,
    apartment,
}: {
    housingCompany: IHousingCompanyDetails;
    apartment: IApartmentDetails | undefined;
}) => {
    const navigate = useNavigate();

    const [saveApartment, {data: saveData, error: saveError, isLoading: isSaveLoading}] = useSaveApartmentMutation();
    const [deleteApartment, {data: deleteData, error: deleteError, isLoading: isDeleteLoading}] =
        useDeleteApartmentMutation();

    // Get all buildings that belong to HousingCompany from RealEstates
    const buildingOptions = housingCompany.real_estates.flatMap((realEstate) => {
        return realEstate.buildings.map((building) => {
            return {label: building.address.street_address, value: building.id};
        });
    });

    // Form
    const initialFormData: IApartmentWritableForm = getInitialFormData(apartment, buildingOptions);

    const formRef = useRef<HTMLFormElement | null>(null);
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
            id: apartment?.id,
            housingCompanyId: housingCompany.id,
        });

        if (!isEditPage) {
            setIsEndModalVisible(true);
        }
    };

    const formOwnershipsList = apartment !== undefined ? apartment.ownerships.map((o) => ({...o, key: uuidv4()})) : [];

    // Flags
    const isEditPage = !!apartment;
    const [isEndModalVisible, setIsEndModalVisible] = useState(false);
    const [isRemoveModalVisible, setIsRemoveModalVisible] = useState(false);

    // Event handlers
    const handleSubmitButtonClick = () => {
        formRef.current && formRef.current.dispatchEvent(new Event("submit", {cancelable: true, bubbles: true}));
    };

    const handleConfirmedRemove = () => {
        deleteApartment({
            id: apartment?.id,
            housingCompanyId: housingCompany.id,
        });
    };

    // Handle remove flow
    useEffect(() => {
        if (isEditPage) {
            if (!isDeleteLoading && !deleteError && deleteData === null) {
                hitasToast("Asunto poistettu onnistuneesti!");
                navigate(`/housing-companies/${housingCompany.id}`);
            } else if (deleteError) {
                setIsRemoveModalVisible(true);
            }
        }
    }, [isDeleteLoading, deleteError, deleteData, navigate, isEditPage, housingCompany.id]);

    // Handle saving flow when editing
    useEffect(() => {
        if (isEditPage) {
            if (!isSaveLoading && !saveError && saveData && saveData.id) {
                hitasToast("Asunto tallennettu onnistuneesti!");
                navigate(`/housing-companies/${saveData.links.housing_company.id}/apartments/${saveData.id}`);
            } else if (saveError) {
                setIsEndModalVisible(true);
            }
        }
    }, [isSaveLoading, saveError, saveData, navigate, isEditPage]);

    return (
        <>
            {apartment ? <ApartmentHeader apartment={apartment} /> : <Heading>Uusi asunto</Heading>}
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
                                value={housingCompany.name.display}
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
                                label="Asuntotyyppi"
                                required
                                queryFunction={useGetApartmentTypesQuery}
                                relatedModelSearchField="value"
                                formObject={formObject}
                                formObjectFieldPath="type"
                                formatFormObjectValue={(obj: ICode) => (obj.id ? obj.value : "")}
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
                        isLoading={isDeleteLoading}
                    />
                )}
                <SaveButton
                    onClick={handleSubmitButtonClick}
                    isLoading={isSaveLoading}
                />
            </div>
            <ConfirmDialogModal
                linkText="Palaa asuntoyhtiön sivulle"
                linkURL={`/housing-companies/${housingCompany.id}`}
                modalText="Haluatko varmasti poistaa asunnon?"
                successText="Asunto poistettu"
                buttonText="Poista"
                isVisible={isRemoveModalVisible}
                setIsVisible={setIsRemoveModalVisible}
                data={deleteData}
                error={deleteError}
                isLoading={isDeleteLoading}
                confirmAction={handleConfirmedRemove}
                cancelAction={() => setIsRemoveModalVisible(false)}
            />
            <SaveDialogModal
                linkText="Asunnon sivulle"
                baseURL={`/housing-companies/${housingCompany.id}/apartments/`}
                isVisible={isEndModalVisible}
                setIsVisible={setIsEndModalVisible}
                data={saveData}
                error={saveError}
                isLoading={isSaveLoading}
            />
        </>
    );
};

const ApartmentCreatePage = () => {
    // Load required data and pass it to the child component
    const params = useParams() as {housingCompanyId: string; apartmentId?: string};
    const isEditPage = !!params.apartmentId;

    const {
        data: housingCompanyData,
        error: housingCompanyError,
        isLoading: isHousingCompanyLoading,
    } = useGetHousingCompanyDetailQuery(params.housingCompanyId);
    const {
        data: apartmentData,
        error: apartmentError,
        isLoading: isApartmentLoading,
    } = useGetApartmentDetailQuery(
        {
            housingCompanyId: params.housingCompanyId,
            apartmentId: params.apartmentId as string,
        },
        {skip: !isEditPage}
    );

    const data = isEditPage ? housingCompanyData && apartmentData : housingCompanyData;
    const error = housingCompanyError || apartmentError;
    const isLoading = isHousingCompanyLoading || (isEditPage && isApartmentLoading);

    return (
        <div className="view--create">
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <LoadedApartmentCreatePage
                    housingCompany={housingCompanyData as IHousingCompanyDetails}
                    apartment={apartmentData as IApartmentDetails}
                />
            </QueryStateHandler>
        </div>
    );
};

export default ApartmentCreatePage;
