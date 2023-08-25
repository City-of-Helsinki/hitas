import {FileInput as HDSFileInput, LoadingSpinner} from "hds-react";
import {useState} from "react";
import {Divider, SaveDialogModal} from "../../../common/components";
import {useSaveExternalSalesDataMutation} from "../../../common/services";
import {hdsToast} from "../../../common/utils";

const Spinner = () => {
    return (
        <div className="spinner-wrap-color">
            <LoadingSpinner />
        </div>
    );
};

const ExternalSalesDataAlreadySaved = () => {
    return (
        <p className="help-text">
            Tilastokeskuksen postinumeroalueiden keskineliöhinnat on tallennettu valitulle Hitas-vuosineljännekselle.
        </p>
    );
};

const ExternalSalesDataImport = ({calculationMonth}) => {
    const [isModalOpen, setIsModalOpen] = useState(false);

    const [saveExternalSalesData, {data, isLoading, error}] = useSaveExternalSalesDataMutation();

    const handleFileSelected = (externalSalesDataFile) => {
        saveExternalSalesData({
            calculation_date: calculationMonth,
            data: externalSalesDataFile,
        })
            .unwrap()
            .then((data) => {
                // Successful upload
                hdsToast.success(
                    `Postinumeroalueiden keskineliöhinnat tallennettu onnistuneesti Hitas-vuosineljännekselle ${data.calculation_quarter}`
                );
            })
            .catch((error) => {
                // eslint-disable-next-line no-console
                console.warn("Caught error:", error);
                setIsModalOpen(true);
            });
    };

    return (
        <>
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
        </>
    );
};

interface ExternalSalesDataImportProps {
    hasRegulationResults: boolean;
    isExternalSalesDataLoading: boolean;
    hasExternalSalesData: boolean;
    calculationMonth: string;
}

const ExternalSalesDataImportSection = ({
    hasRegulationResults,
    isExternalSalesDataLoading,
    hasExternalSalesData,
    calculationMonth,
}: ExternalSalesDataImportProps) => {
    if (hasRegulationResults) {
        return null;
    }

    let sectionContent;
    if (isExternalSalesDataLoading) {
        sectionContent = <Spinner />;
    } else if (hasExternalSalesData) {
        sectionContent = <ExternalSalesDataAlreadySaved />;
    } else {
        sectionContent = <ExternalSalesDataImport calculationMonth={calculationMonth} />;
    }

    return (
        <>
            <Divider size="l" />
            <div className="external-sales-data-import-section">{sectionContent}</div>
        </>
    );
};

export default ExternalSalesDataImportSection;
