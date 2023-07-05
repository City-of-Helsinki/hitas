import {Dialog} from "hds-react";
import {useState} from "react";
import {useForm} from "react-hook-form";
import {useParams} from "react-router-dom";
import {useCreateFromSalesCatalogMutation, useValidateSalesCatalogMutation} from "../../../app/services";
import {CloseButton, QueryStateHandler, SaveButton} from "../../../common/components";
import {FileInput} from "../../../common/components/form";
import {ErrorResponse, ISalesCatalogApartment} from "../../../common/schemas";
import {hdsToast} from "../../../common/utils";

const SalesCatalogImport = () => {
    const [isImportModalOpen, setIsImportModalOpen] = useState(false);
    const [fileValidationError, setFileValidationError] = useState<ErrorResponse>();
    const [isFileValid, setisFileValid] = useState(false);
    const params = useParams() as {readonly housingCompanyId: string};
    const salesCatalogForm = useForm({defaultValues: {salesCatalog: null}});
    const [validateSalesCatalog, {data: validateData, isLoading: isValidating, error: validateError}] =
        useValidateSalesCatalogMutation();
    const [createImportedApartments, {error: createError}] = useCreateFromSalesCatalogMutation();
    const handleCreateButton = () => {
        const importedApartments: object[] = [];
        validateData.apartments.forEach((apartment: ISalesCatalogApartment) => {
            importedApartments.push({
                stair: apartment.stair,
                floor: apartment.floor,
                apartment_number: apartment.apartment_number,
                rooms: apartment.rooms,
                apartment_type: (apartment.apartment_type as {id: string}).id,
                surface_area: apartment.surface_area,
                share_number_start: apartment.share_number_start,
                share_number_end: apartment.share_number_end,
                catalog_purchase_price: apartment.catalog_purchase_price,
                catalog_primary_loan_amount: apartment.catalog_primary_loan_amount,
            });
        });
        createImportedApartments({
            data: importedApartments,
            housingCompanyId: params.housingCompanyId,
        })
            .unwrap()
            .then(() => {
                hdsToast.success("Asuntojen tuonti onnistui.");
                setIsImportModalOpen(false);
            })
            .catch((e) => {
                hdsToast.error("Asuntojen tuonti epäonnistui: " + e.message);
                // eslint-disable-next-line no-console
                console.warn(e, createError);
            });
    };
    const validateFile = (data) => {
        setFileValidationError(undefined);
        validateSalesCatalog({
            data: data.salesCatalog,
            housingCompanyId: params.housingCompanyId,
        })
            .unwrap()
            .then(() => {
                setisFileValid(true);
            })
            // eslint-disable-next-line no-console
            .catch((e) => {
                setisFileValid(false);
                setFileValidationError(e.data);
            })
            .finally(() => {
                setIsImportModalOpen(true);
            });
    };
    return (
        <div>
            <FileInput
                buttonLabel="Lataa myyntihintaluettelo"
                name="salesCatalog"
                formObject={salesCatalogForm}
                accept=".xlsx"
                onChange={() => validateFile(salesCatalogForm.getValues())}
            />
            <Dialog
                id="import-sales-catalog-modal"
                aria-labelledby="Sales catalog import modal"
                isOpen={isImportModalOpen}
                className={fileValidationError ? "error-modal" : undefined}
            >
                <Dialog.Header
                    id="import-sales-catalog-modal"
                    title="Myyntihintaluettelon lataus"
                />
                <Dialog.Content>
                    {!fileValidationError ? (
                        <>
                            <p>Luodaanko myyntihintaluettelon pohjalta seuraavat asunnot:</p>
                            <QueryStateHandler
                                data={validateData}
                                error={validateError}
                                isLoading={isValidating}
                            >
                                <div className="sales-catalog-import-list">
                                    <div className="list-headers">
                                        <div>Porras</div>
                                        <div>Huoneisto</div>
                                        <div>Kerros</div>
                                        <div>Tyyppi</div>
                                        <div>Pinta-ala</div>
                                        <div>Osakenumerot</div>
                                    </div>
                                    {validateData && validateData?.apartments.length > 0 && (
                                        <ul>
                                            {validateData?.apartments.map((apartment: ISalesCatalogApartment) => (
                                                <li key={apartment.row.toString()}>
                                                    <div>{apartment.stair}</div>
                                                    <div>{apartment.apartment_number}</div>
                                                    <div>{apartment.floor}</div>
                                                    <div>
                                                        {apartment.rooms}{" "}
                                                        {(apartment.apartment_type as {value: string}).value}
                                                    </div>
                                                    <div>{apartment.surface_area}</div>
                                                    <div>{`${apartment.share_number_start} - ${apartment.share_number_end}`}</div>
                                                </li>
                                            ))}
                                        </ul>
                                    )}
                                </div>
                            </QueryStateHandler>
                        </>
                    ) : (
                        <>
                            <h2>
                                {fileValidationError && (fileValidationError as unknown as {message: string})?.message}
                            </h2>
                            <p>
                                Luetteloa ei voitu ladata, koska siinä havaittiin virheitä
                                {fileValidationError?.fields ? ":" : "."}
                            </p>
                            {fileValidationError?.fields?.length && fileValidationError?.fields?.length > 0 ? (
                                <ul className="field-error-list">
                                    {fileValidationError?.fields?.map((field) => (
                                        <li key={field.field}>
                                            <span>{field.field}</span>
                                            <span>{field.message}</span>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p>{fileValidationError?.message}</p>
                            )}
                        </>
                    )}
                </Dialog.Content>
                <Dialog.ActionButtons>
                    <CloseButton onClick={() => setIsImportModalOpen(false)} />
                    {isFileValid && (
                        <SaveButton
                            onClick={() => handleCreateButton()}
                            buttonText="Luo asunnot"
                        />
                    )}
                </Dialog.ActionButtons>
            </Dialog>
        </div>
    );
};

export default SalesCatalogImport;
