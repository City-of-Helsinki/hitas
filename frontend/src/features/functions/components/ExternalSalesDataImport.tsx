import {useState} from "react";
import {useForm} from "react-hook-form";
import {useSaveExternalSalesDataMutation} from "../../../app/services";
import {SaveDialogModal} from "../../../common/components";
import {FileInput} from "../../../common/components/form";
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
    const {watch, handleSubmit} = formObject;
    const formFile: File | undefined = watch("file");
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
        <form
            className={`file${formFile === undefined ? "" : " file--selected"}`}
            onSubmit={handleSubmit(onSubmit)}
        >
            <FileInput
                name="file"
                id="file-input"
                buttonLabel="Valitse tiedosto"
                formObject={formObject}
                label="Syötä postinumeroalueiden keskineliöhinnat"
                tooltipText="Tilastokeskukselta saatu excel-tiedosto (.xslx)"
                onChange={() => onSubmit(formObject.getValues())}
            />
            <SaveDialogModal
                title="Tallennetaan excel-tiedostoa"
                data={data}
                error={error}
                isLoading={isLoading}
                isVisible={isModalOpen}
                setIsVisible={setIsModalOpen}
            />
        </form>
    );
}
