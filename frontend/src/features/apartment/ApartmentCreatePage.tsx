import {useContext, useEffect, useRef, useState} from "react";

import {zodResolver} from "@hookform/resolvers/zod";
import {Fieldset} from "hds-react";
import {SubmitHandler, useForm} from "react-hook-form";
import {useNavigate} from "react-router-dom";

import {
    ConfirmDialogModal,
    DeleteButton,
    NavigateBackButton,
    SaveButton,
    SaveDialogModal,
} from "../../common/components";
import {
    DateInput,
    FormProviderForm,
    NumberInput,
    RelatedModelInput,
    SelectInput,
    TextAreaInput,
    TextInput,
} from "../../common/components/forms";
import {
    ApartmentWritableFormSchema,
    errorMessages,
    IApartmentDetails,
    IApartmentWritable,
    IApartmentWritableForm,
    ICode,
} from "../../common/schemas";
import {useDeleteApartmentMutation, useGetApartmentTypesQuery, useSaveApartmentMutation} from "../../common/services";
import {hdsToast, isEmpty, setAPIErrorsForFormFields} from "../../common/utils";
import {ApartmentViewContext, ApartmentViewContextProvider} from "./components/ApartmentViewContextProvider";

const ApartmentDeleteButton = ({apartment}) => {
    const navigate = useNavigate();

    const [deleteApartment, {data: deleteData, error: deleteError, isLoading: isDeleteLoading}] =
        useDeleteApartmentMutation();

    const [isDeleteModalVisible, setIsDeleteModalVisible] = useState(false);

    const handleConfirmedDeleteAction = () => {
        deleteApartment({
            id: apartment.id,
            housingCompanyId: apartment.links.housing_company.id,
        })
            .unwrap()
            .then(() => {
                hdsToast.info("Asunto poistettu onnistuneesti!");
                navigate(`/housing-companies/${apartment.links.housing_company.id}`);
            })
            .catch(() => {
                hdsToast.error("Virhe poistaessa asuntoa!");
                setIsDeleteModalVisible(true);
            });
    };

    return (
        <>
            <DeleteButton
                onClick={() => setIsDeleteModalVisible(true)}
                isLoading={isDeleteLoading}
            />
            <ConfirmDialogModal
                linkText="Palaa taloyhtiön sivulle"
                linkURL={`/housing-companies/${apartment.links.housing_company.id}`}
                modalText="Haluatko varmasti poistaa asunnon?"
                successText="Asunto poistettu"
                buttonText="Poista"
                isVisible={isDeleteModalVisible}
                setIsVisible={setIsDeleteModalVisible}
                data={deleteData}
                error={deleteError}
                isLoading={isDeleteLoading}
                confirmAction={handleConfirmedDeleteAction}
                cancelAction={() => setIsDeleteModalVisible(false)}
            />
        </>
    );
};

const getInitialFormData = (apartment, buildingOptions): IApartmentWritableForm => {
    if (apartment) {
        return convertApartmentDetailToWritable(apartment);
    } else {
        return {
            type: null,
            surface_area: null,
            rooms: null,
            shares: {start: undefined, end: undefined},
            address: {
                apartment_number: undefined,
                floor: null,
                stair: "",
            },
            completion_date: null,
            prices: {
                construction: {
                    loans: null,
                    interest: {
                        rate_mpi: undefined,
                        rate_cpi: undefined,
                    },
                    debt_free_purchase_price: null,
                    additional_work: null,
                },
                updated_acquisition_price: null,
            },
            // The first building in the list is selected by default
            building: buildingOptions.length
                ? {label: buildingOptions[0].label, value: buildingOptions[0].value}
                : {label: "", value: ""},
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
        shares: apartment.shares
            ? {start: apartment.shares.start, end: apartment.shares.end}
            : {start: undefined, end: undefined},
        building: {label: apartment.links.building.street_address, value: apartment.links.building.id},
    };
};

const formatApartmentFormDataForSubmit = (apartment, data): IApartmentWritable => {
    return {
        ...data,
        // Copy street_address from selected building
        address: {...data.address, street_address: data.building.label},
        building: {id: data.building.value},

        // Clean share fields
        shares: {
            start: data.shares?.start ?? null,
            end: data.shares?.end ?? null,
        },
    };
};

const LoadedApartmentCreatePage = () => {
    const navigate = useNavigate();
    const {housingCompany, apartment} = useContext(ApartmentViewContext);

    const [saveApartment, {data: apartmentSaveData, error: apartmentSaveError, isLoading: isApartmentSaveLoading}] =
        useSaveApartmentMutation();

    // Flags
    const isEditPage = !!apartment;
    const [isEndModalVisible, setIsEndModalVisible] = useState(false);

    // Get all buildings that belong to HousingCompany from RealEstates
    const buildingOptions = housingCompany.real_estates.flatMap((realEstate) => {
        return realEstate.buildings.map((building) => {
            return {label: building.address.street_address, value: building.id};
        });
    });

    // Form
    const initialFormData: IApartmentWritableForm = getInitialFormData(apartment, buildingOptions);
    const formRef = useRef<HTMLFormElement>(null);
    const formObject = useForm<IApartmentWritableForm>({
        defaultValues: initialFormData,
        mode: "onBlur",
        resolver: zodResolver(ApartmentWritableFormSchema),
    });

    const onSubmit: SubmitHandler<IApartmentWritableForm> = (data) => {
        const formattedFormData = formatApartmentFormDataForSubmit(apartment, data);

        saveApartment({
            data: formattedFormData,
            id: apartment?.id,
            housingCompanyId: housingCompany.id,
        })
            .unwrap()
            .then((payload) => {
                hdsToast.success("Asunto tallennettu onnistuneesti!");
                if (!isEditPage) {
                    setIsEndModalVisible(true);
                } else {
                    navigate(`/housing-companies/${housingCompany.id}/apartments/${payload.id}`);
                }
            })
            .catch((error) => {
                hdsToast.error("Asunnon tallentaminen epäonnistui!");
                setIsEndModalVisible(true);
                setAPIErrorsForFormFields(formObject, error);
            });
    };

    const handleValidateShares = (start, end) => {
        // Form-level validation for shares
        if (start === null && end === null) {
            formObject.clearErrors("shares");
        }
        // If either start or end is null, we have an error
        else if (!start) {
            formObject.setError("shares.start", {type: "custom", message: errorMessages.sharesEmpty});
        } else if (!end) {
            formObject.setError("shares.end", {type: "custom", message: errorMessages.sharesEmpty});
        }
        // If start is greater than end, we have an error
        else if (start && end && start >= end) {
            formObject.setError("shares.start", {type: "custom", message: errorMessages.sharesStartGreaterThanEnd});
            formObject.setError("shares.end", {type: "custom", message: errorMessages.sharesStartGreaterThanEnd});
        } else {
            // If we got so far, there were no errors, clear any remaining shares errors away.
            formObject.clearErrors("shares");
        }
    };

    const handleValidateInterestDuringConstructionRates = (rate6, rate14) => {
        // Form-level validation for interest rates during construction
        if (rate6 === null && rate14 === null) {
            formObject.clearErrors("prices.construction.interest");
        }
        // If either interest rate is null, we have an error
        else if (!rate6 && rate6 !== 0) {
            formObject.setError("prices.construction.interest.rate_mpi", {
                type: "custom",
                message: errorMessages.constructionInterestEmpty,
            });
        } else if (!rate14 && rate14 !== 0) {
            formObject.setError("prices.construction.interest.rate_cpi", {
                type: "custom",
                message: errorMessages.constructionInterestEmpty,
            });
        }
        // If MPI is greater than CPI, we have an error (CPI interest should always be equal or greater than MPI)
        else if (rate6 && rate14 && rate6 > rate14) {
            formObject.setError("prices.construction.interest.rate_mpi", {
                type: "custom",
                message: errorMessages.constructionInterest6GreaterThan14,
            });
            formObject.setError("prices.construction.interest.rate_cpi", {
                type: "custom",
                message: errorMessages.constructionInterest6GreaterThan14,
            });
        } else {
            // If we got so far, there were no errors, clear any remaining interest rate errors away.
            formObject.clearErrors("prices.construction.interest");
        }
    };

    // Event handlers
    const handleFormPreSubmitValidationSubmit = () => {
        // Recursively find the first error in the form (The error may be nested, e.g. shares.start)
        const getFirstError = (errors, _fullPath = "") => {
            if (isEmpty(errors)) return null;
            const firstKey = Object.keys(errors)[0];
            const firstError = errors[firstKey];
            if (firstError.type) {
                return `${_fullPath}${firstKey}`;
            }
            return getFirstError(firstError, `${_fullPath}${firstKey}.`);
        };

        handleValidateShares(...formObject.getValues(["shares.start", "shares.end"]));
        handleValidateInterestDuringConstructionRates(
            ...formObject.getValues(["prices.construction.interest.rate_mpi", "prices.construction.interest.rate_cpi"])
        );

        // If there are errors, set focus to the first error field
        const firstError = getFirstError(formObject.formState.errors);
        if (firstError && firstError !== "root") {
            formObject.setFocus(firstError);
            return; // Don't submit the form if there are errors
        }

        formRef.current && formRef.current.dispatchEvent(new Event("submit", {cancelable: true, bubbles: true}));
    };

    const watch = formObject.watch;
    useEffect(() => {
        const subscription = watch((value, {name}) => {
            if (name === "shares.start" || name === "shares.end") {
                handleValidateShares(value?.shares?.start, value.shares?.end);
            }

            if (name === "prices.construction.interest.rate_mpi" || name === "prices.construction.interest.rate_cpi") {
                handleValidateInterestDuringConstructionRates(
                    value?.prices?.construction?.interest?.rate_mpi,
                    value?.prices?.construction?.interest?.rate_cpi
                );
            }
        });
        return () => subscription.unsubscribe();
        // eslint-disable-next-line
    }, [watch]);

    return (
        <>
            <FormProviderForm
                formObject={formObject}
                formRef={formRef}
                onSubmit={onSubmit}
            >
                <div className="field-sets">
                    <Fieldset heading="">
                        <div className="row">
                            <SelectInput
                                label="Rakennus"
                                options={buildingOptions || []}
                                name="building"
                                defaultValue={initialFormData.building.value}
                                required
                            />
                        </div>
                        <div className="row">
                            <TextInput
                                name="address.stair"
                                label="Rappu"
                                required
                            />
                            <NumberInput
                                name="address.apartment_number"
                                label="Asunnon numero"
                                required
                            />
                        </div>
                        <div className="row">
                            <NumberInput
                                name="address.floor"
                                label="Kerros"
                            />
                            <NumberInput
                                name="surface_area"
                                label="Pinta-ala"
                                allowDecimals
                                unit="m²"
                            />
                        </div>
                        <div className="row">
                            <NumberInput
                                name="rooms"
                                label="Huoneiden määrä"
                            />
                            <RelatedModelInput
                                label="Asuntotyyppi"
                                name="type"
                                queryFunction={useGetApartmentTypesQuery}
                                relatedModelSearchField="value"
                                transform={(obj: ICode) => obj.value}
                            />
                        </div>
                        <div className="row">
                            <DateInput
                                label="Valmistumispäivä"
                                name="completion_date"
                            />
                            <NumberInput
                                label="Päivitetty hankinta-arvo (€)"
                                name="prices.updated_acquisition_price"
                                allowDecimals
                            />
                        </div>
                    </Fieldset>
                    <Fieldset heading="">
                        <div className="row">
                            <NumberInput
                                name="shares.start"
                                label="Osakkeet, alku"
                            />
                            <NumberInput
                                name="shares.end"
                                label="Osakkeet, loppu"
                            />
                        </div>
                        <div className="row">
                            <NumberInput
                                name="prices.construction.loans"
                                label="Rakennusaikaiset lainat"
                                unit="€"
                                allowDecimals
                            />
                            <NumberInput
                                name="prices.construction.interest.rate_mpi"
                                label="Rak.aik. korko (MHI)"
                                unit="€"
                                allowDecimals
                            />
                            <NumberInput
                                name="prices.construction.interest.rate_cpi"
                                label="Rak.aik. korko (RKI)"
                                unit="€"
                                allowDecimals
                            />
                        </div>
                        <div className="row">
                            <NumberInput
                                name="prices.construction.additional_work"
                                label="Rakennusaikaiset lisätyöt"
                                unit="€"
                                allowDecimals
                            />
                            {apartment?.prices?.construction.debt_free_purchase_price ? (
                                <NumberInput
                                    name="prices.construction.debt_free_purchase_price"
                                    label="Luovutushinta (RA)"
                                    unit="€"
                                    allowDecimals
                                />
                            ) : (
                                <div />
                            )}
                        </div>
                        <div className="row">
                            <TextAreaInput
                                name="notes"
                                label="Muistiinpanot"
                            />
                        </div>
                    </Fieldset>
                </div>
            </FormProviderForm>
            <div className="row row--buttons">
                <NavigateBackButton />
                {isEditPage && <ApartmentDeleteButton apartment={apartment} />}
                <SaveButton
                    onClick={handleFormPreSubmitValidationSubmit}
                    isLoading={isApartmentSaveLoading}
                />
            </div>
            <SaveDialogModal
                linkText="Asunnon sivulle"
                baseURL={`/housing-companies/${housingCompany.id}/apartments/`}
                isVisible={isEndModalVisible}
                setIsVisible={setIsEndModalVisible}
                data={apartmentSaveData}
                error={apartmentSaveError}
                isLoading={isApartmentSaveLoading}
            />
        </>
    );
};

const ApartmentCreatePage = () => {
    return (
        <ApartmentViewContextProvider viewClassName="view--create">
            <LoadedApartmentCreatePage />
        </ApartmentViewContextProvider>
    );
};

export default ApartmentCreatePage;
