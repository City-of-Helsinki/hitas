import {useContext, useEffect, useRef, useState} from "react";

import {zodResolver} from "@hookform/resolvers/zod";
import {Fieldset} from "hds-react";
import {SubmitHandler, useForm} from "react-hook-form";
import {useNavigate} from "react-router-dom";

import {useDeleteApartmentMutation, useGetApartmentTypesQuery, useSaveApartmentMutation} from "../../app/services";
import {
    ConfirmDialogModal,
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
import {
    ApartmentWritableFormSchema,
    errorMessages,
    IApartmentDetails,
    IApartmentWritable,
    IApartmentWritableForm,
    ICode,
} from "../../common/schemas";
import {hdsToast, isEmpty} from "../../common/utils";
import ApartmentViewContextProvider, {ApartmentViewContext} from "./components/ApartmentViewContextProvider";

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
                hdsToast.success("Asunto poistettu onnistuneesti!");
                navigate(`/housing-companies/${apartment.links.housing_company.id}`);
            })
            .catch(() => {
                hdsToast.error("Virhe poistaessa asuntoa!");
                setIsDeleteModalVisible(true);
            });
    };

    return (
        <>
            <RemoveButton
                onClick={() => setIsDeleteModalVisible(true)}
                isLoading={isDeleteLoading}
                buttonText="Poista"
            />
            <ConfirmDialogModal
                linkText="Palaa asuntoyhtiön sivulle"
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
                        rate_6: undefined,
                        rate_14: undefined,
                    },
                    debt_free_purchase_price: null,
                    additional_work: null,
                },
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

    const [saveApartment, {data: saveData, error: saveError, isLoading: isSaveLoading}] = useSaveApartmentMutation();

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
    const formRef = useRef<HTMLFormElement | null>(null);
    const formObject = useForm<IApartmentWritableForm>({
        defaultValues: initialFormData,
        mode: "onBlur",
        resolver: zodResolver(ApartmentWritableFormSchema),
    });

    // Set errors returned from the API for form fields
    const setAPIErrorsForFormFields = (error) => {
        if (error?.data?.fields) {
            for (const fieldError of error.data.fields) {
                formObject.setError(fieldError.field, {type: "custom", message: fieldError.message});
            }
        }
    };

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
                setAPIErrorsForFormFields(error);
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
            formObject.setError("prices.construction.interest.rate_6", {
                type: "custom",
                message: errorMessages.constructionInterestEmpty,
            });
        } else if (!rate14 && rate14 !== 0) {
            formObject.setError("prices.construction.interest.rate_14", {
                type: "custom",
                message: errorMessages.constructionInterestEmpty,
            });
        }
        // If 6% is greater than 14%, we have an error
        else if (rate6 && rate14 && rate6 >= rate14) {
            formObject.setError("prices.construction.interest.rate_6", {
                type: "custom",
                message: errorMessages.constructionInterest6GreaterThan14,
            });
            formObject.setError("prices.construction.interest.rate_14", {
                type: "custom",
                message: errorMessages.constructionInterest6GreaterThan14,
            });
        } else {
            // If we got so far, there were no errors, clear any remaining interest rate errors away.
            formObject.clearErrors("prices.construction.interest");
        }
    };

    // Event handlers
    const handleFormSubmit = () => {
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
            ...formObject.getValues(["prices.construction.interest.rate_6", "prices.construction.interest.rate_14"])
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

            if (name === "prices.construction.interest.rate_6" || name === "prices.construction.interest.rate_14") {
                handleValidateInterestDuringConstructionRates(
                    value?.prices?.construction?.interest?.rate_6,
                    value?.prices?.construction?.interest?.rate_14
                );
            }
        });
        return () => subscription.unsubscribe();
        // eslint-disable-next-line
    }, [watch]);

    return (
        <>
            <form
                ref={formRef}
                // eslint-disable-next-line no-console
                onSubmit={formObject.handleSubmit(onSubmit, (errors) => console.warn(formObject, errors))}
            >
                <div className="field-sets">
                    <Fieldset heading="">
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
                                allowDecimals
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
                                queryFunction={useGetApartmentTypesQuery}
                                relatedModelSearchField="value"
                                formObject={formObject}
                                formObjectFieldPath="type"
                                formatFormObjectValue={(obj: ICode) => (obj?.id ? obj.value : "")}
                            />
                        </div>
                        <div className="row">
                            <DateInput
                                label="Valmistumispäivä"
                                name="completion_date"
                                formObject={formObject}
                            />
                            <div />
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
                                allowDecimals
                                formObject={formObject}
                            />
                            <NumberInput
                                name="prices.construction.interest.rate_6"
                                label="Rak.aik. korko (6%)"
                                unit="€"
                                allowDecimals
                                formObject={formObject}
                            />
                            <NumberInput
                                name="prices.construction.interest.rate_14"
                                label="Rak.aik. korko (14%)"
                                unit="€"
                                allowDecimals
                                formObject={formObject}
                            />
                        </div>
                        <div className="row">
                            <NumberInput
                                name="prices.construction.additional_work"
                                label="Rakennusaikaiset lisätyöt"
                                unit="€"
                                allowDecimals
                                formObject={formObject}
                            />
                            {apartment?.prices?.construction.debt_free_purchase_price ? (
                                <NumberInput
                                    name="prices.construction.debt_free_purchase_price"
                                    label="Luovutushinta (RA)"
                                    unit="€"
                                    allowDecimals
                                    formObject={formObject}
                                />
                            ) : (
                                <div />
                            )}
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
                {isEditPage && <ApartmentDeleteButton apartment={apartment} />}
                <SaveButton
                    onClick={handleFormSubmit}
                    isLoading={isSaveLoading}
                />
            </div>
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
    return (
        <ApartmentViewContextProvider viewClassName="view--create">
            <LoadedApartmentCreatePage />
        </ApartmentViewContextProvider>
    );
};

export default ApartmentCreatePage;
