import {useState} from "react";
import {FormProvider, useForm} from "react-hook-form";
import {SaveDialogModal} from "../../../common/components";
import {FileInput, FormProviderForm} from "../../../common/components/forms";
import {useSaveExternalSalesDataMutation} from "../../../common/services";
import {hdsToast} from "../../../common/utils";

export default function ExternalSalesDataImport({formDate}) {
    const [isModalOpen, setIsModalOpen] = useState(false);

    const [saveExternalSalesData, {data, isLoading, error}] = useSaveExternalSalesDataMutation();

    const formObject = useForm({
        defaultValues: {
            calculationDate: formDate,
            file: undefined,
        },
        mode: "all",
    });

    const formFile: File | undefined = formObject.watch("file");

    // Submit = upload file
    const onSubmit = (data) => {
        const fileWithDate = {
            data: data.file,
            calculation_date: formDate,
        };
        saveExternalSalesData(fileWithDate)
            .unwrap()
            .then((data) => {
                if ("error" in (data as object)) {
                    // eslint-disable-next-line no-console
                    console.warn("Uncaught error:", data.error);
                    setIsModalOpen(true);
                } else {
                    // Successful upload
                    hdsToast.success("Postinumeroalueiden keskinumerohinnat ladattu onnistuneesti");
                    formObject.setValue("file", undefined, {shouldValidate: true});
                }
            })
            .catch((error) => {
                // eslint-disable-next-line no-console
                console.warn("Caught error:", error);
                setIsModalOpen(true);
            });
    };

    return (
        <FormProviderForm
            formObject={formObject}
            onSubmit={onSubmit}
            className={`file${formFile === undefined ? "" : " file--selected"}`}
        >
            <FormProvider {...formObject}>
                <FileInput
                    name="file"
                    buttonLabel="Valitse tiedosto"
                    label="Postinumeroalueiden keskineliöhinnat *"
                    tooltipText="Tilastokeskukselta saatu excel-tiedosto (.xslx)"
                    accept=".xlsx"
                    onChange={() => onSubmit(formObject.getValues())}
                />
            </FormProvider>
            <SaveDialogModal
                title="Tallennetaan excel-tiedostoa"
                data={data}
                error={error}
                isLoading={isLoading}
                isVisible={isModalOpen}
                setIsVisible={setIsModalOpen}
            />
        </FormProviderForm>
    );
}
