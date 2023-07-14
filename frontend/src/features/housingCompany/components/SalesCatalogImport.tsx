import {Dialog, Table} from "hds-react";
import {useState} from "react";
import {FormProvider, useForm} from "react-hook-form";
import {useParams} from "react-router-dom";
import {useCreateFromSalesCatalogMutation, useValidateSalesCatalogMutation} from "../../../app/services";
import {CloseButton, QueryStateHandler, SaveButton} from "../../../common/components";
import {FileInput} from "../../../common/components/forms";
import {ErrorResponse, ISalesCatalogApartment} from "../../../common/schemas";
import {hdsToast} from "../../../common/utils";

const tableTheme = {
    "--header-background-color": "var(--color-black-80)",
};

const SalesCatalogImport = () => {
    const [isImportModalOpen, setIsImportModalOpen] = useState(false);
    const [fileValidationError, setFileValidationError] = useState<ErrorResponse | undefined>();

    const params = useParams() as {readonly housingCompanyId: string};

    const formObject = useForm({defaultValues: {salesCatalog: null}});
    const [validateSalesCatalog, {data: validateData, isLoading: isValidating, error: validateError}] =
        useValidateSalesCatalogMutation();

    const [createImportedApartments, {error: createError}] = useCreateFromSalesCatalogMutation();

    const handleCreateButton = () => {
        const importedApartments: object[] = [];
        validateData.apartments.forEach((apartment: ISalesCatalogApartment) => {
            importedApartments.push({
                ...apartment,
                apartment_type: (apartment.apartment_type as {id: string}).id,
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
        validateSalesCatalog({
            data: data.salesCatalog,
            housingCompanyId: params.housingCompanyId,
        })
            .unwrap()
            .then(() => {
                setFileValidationError(undefined);
            })
            // eslint-disable-next-line no-console
            .catch((e) => {
                setFileValidationError(e.data);
            })
            .finally(() => {
                setIsImportModalOpen(true);
            });
    };

    return (
        <>
            <FormProvider {...formObject}>
                <FileInput
                    buttonLabel="Lataa myyntihintaluettelo"
                    name="salesCatalog"
                    accept=".xlsx"
                    onChange={() => validateFile(formObject.getValues())}
                />
            </FormProvider>
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
                                    <Table
                                        id="sales-catalog-import-table"
                                        cols={[
                                            {key: "stair", headerName: "Porras"},
                                            {key: "apartment_number", headerName: "Huoneisto"},
                                            {key: "floor", headerName: "Kerros"},
                                            {
                                                key: "rooms",
                                                headerName: "Tyyppi",
                                                transform: (obj) => `${obj.rooms} ${obj.apartment_type.value}`,
                                            },
                                            {key: "surface_area", headerName: "Pinta-ala"},
                                            {
                                                key: "share_number_start",
                                                headerName: "Osakenumerot",
                                                transform: (obj) =>
                                                    `${obj.share_number_start} - ${obj.share_number_end}`,
                                            },
                                        ]}
                                        rows={validateData?.apartments}
                                        indexKey="apartment_number"
                                        dense
                                        zebra
                                        theme={tableTheme}
                                    />
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
                    {!fileValidationError && (
                        <SaveButton
                            onClick={() => handleCreateButton()}
                            buttonText="Luo asunnot"
                        />
                    )}
                </Dialog.ActionButtons>
            </Dialog>
        </>
    );
};

export default SalesCatalogImport;
