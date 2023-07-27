import {FileInput as HDSFileInput} from "hds-react";
import {useState} from "react";
import {SaveDialogModal} from "../../../common/components";
import {useSaveExternalSalesDataMutation} from "../../../common/services";
import {hdsToast} from "../../../common/utils";

const ExternalSalesDataImport = ({calculationMonth}) => {
    const [isModalOpen, setIsModalOpen] = useState(false);

    const [saveExternalSalesData, {data, isLoading, error}] = useSaveExternalSalesDataMutation();

    // Upload file to backend
    const handleFileSelected = (externalSalesDataFile) => {
        saveExternalSalesData({
            calculation_date: formDate,
            data: externalSalesDataFile,
        })
            .unwrap()
            .then((data) => {
                // Successful upload
                hdsToast.success(
                    `Postinumeroalueiden keskineliöhinnat ladattu onnistuneesti Hitas-vuosineljännekselle ${data.calculation_quarter}`
                );
            })
            .catch((error) => {
                // eslint-disable-next-line no-console
                console.warn("Caught error:", error);
                setIsModalOpen(true);
            });
    };

    return (
        <div className="external-sales-data-import">
            <HDSFileInput
                id="externalSalesDataFile"
                label="Tilastokeskuksen postinumeroalueiden keskineliöhinnat"
                tooltipText="Syötä valitun Hitas-vuosinejänneksen tilastokeskukselta saatu excel-tiedosto, joka sisältää Helsingin postinumeroalueiden keskineliöhinnat"
                buttonLabel="Valitse tiedosto"
                onChange={(files) => {
                    if (files.length !== 0) {
                        handleFileSelected(files[0]);
                    }
                }}
                accept=".xlsx"
                multiple={false}
                required
            />
            <SaveDialogModal
                title="Tallennetaan excel-tiedostoa"
                data={data}
                error={error}
                isLoading={isLoading}
                isVisible={isModalOpen}
                setIsVisible={setIsModalOpen}
            />
        </div>
    );
};

export default ExternalSalesDataImport;