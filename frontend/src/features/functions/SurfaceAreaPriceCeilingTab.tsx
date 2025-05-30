import {Button, ButtonPresetTheme, ErrorSummary, IconCogwheels, LoadingSpinner} from "hds-react";

import {useState} from "react";
import {
    Divider,
    DownloadButton,
    GenericActionModal,
    Heading,
    QueryStateHandler,
    SurfaceAreaPriceCeilingTable,
} from "../../common/components";
import {
    downloadSurfaceAreaPriceCeilingResults,
    useCalculatePriceCeilingMutation,
    useGetIndicesQuery,
} from "../../common/services";
import {getHitasQuarterFullLabel, hdsToast, today} from "../../common/utils";

const DownloadSurfaceAreaPriceCeilingResultsButton = ({extraOnClickAction}: {extraOnClickAction?}) => {
    const currentMonth = today().slice(0, 7);

    return (
        <DownloadButton
            onClick={() => {
                downloadSurfaceAreaPriceCeilingResults(currentMonth + "-01");
                extraOnClickAction && extraOnClickAction();
            }}
            buttonText="Lataa laskentaraportti"
        />
    );
};

const CalculateSurfaceAreaPriceCeilingButton = ({
    isCurrentQuarterCalculated,
    handleCalculateButtonOnClick,
    isLoading,
}) => {
    return (
        <Button
            theme={ButtonPresetTheme.Black}
            onClick={handleCalculateButtonOnClick}
            iconStart={isLoading ? <LoadingSpinner small /> : <IconCogwheels />}
        >
            {isCurrentQuarterCalculated ? "Laske rajaneliöhinta uudelleen" : "Laske rajaneliöhinta"}
        </Button>
    );
};

const CurrentMonthCalculationExists = ({
    sapcIndexData,
    isCurrentQuarterCalculated,
    handleCalculateButtonOnClick,
    isLoading,
}) => {
    const currentMonth = today().slice(0, 7);

    return (
        <>
            <div className="surface-area-price-ceiling-value">
                <label>Rajaneliöhinta {getHitasQuarterFullLabel(currentMonth)}</label>
                <span>{sapcIndexData.contents[0].value}</span>
            </div>
            <CalculateSurfaceAreaPriceCeilingButton
                isCurrentQuarterCalculated={isCurrentQuarterCalculated}
                handleCalculateButtonOnClick={handleCalculateButtonOnClick}
                isLoading={isLoading}
            />
        </>
    );
};

const CurrentMonthCalculationMissing = ({isCurrentQuarterCalculated, handleCalculateButtonOnClick, isLoading}) => {
    const currentMonth = today().slice(0, 7);

    return (
        <>
            <p>
                Tälle Hitas-neljännekselle <b>{getHitasQuarterFullLabel(currentMonth)}</b> ei vielä ole laskettu
                rajaneliöhintaa.
            </p>
            <CalculateSurfaceAreaPriceCeilingButton
                isCurrentQuarterCalculated={isCurrentQuarterCalculated}
                handleCalculateButtonOnClick={handleCalculateButtonOnClick}
                isLoading={isLoading}
            />
        </>
    );
};

const SurfaceAreaPriceCeilingCalculationSection = ({sapcIndexData}) => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const closeModal = () => setIsModalOpen(false);

    const [calculatePriceCeiling, {data: calculationData, isLoading, error}] = useCalculatePriceCeilingMutation();

    const handleCalculateButtonOnClick = () => {
        calculatePriceCeiling({calculation_date: currentMonth + "-01"})
            .unwrap()
            .then(() => {
                hdsToast.success("Rajahinnan laskenta onnistui");
                setIsModalOpen(true);
            })
            .catch((error) => {
                hdsToast.error("Rajahinnan laskenta epäonnistui");
                // eslint-disable-next-line no-console
                console.error(error);
            });
    };

    const currentMonth = today().slice(0, 7);

    // Check if SAPC for current month is already calculated
    const isCurrentQuarterCalculated = sapcIndexData.contents.some((item) => item.month === currentMonth);

    return (
        <>
            {error && (
                <ErrorSummary label={(error as {data: {message: string}})?.data?.message}>
                    {(error as {data: {fields: [{field: string; message: string}]}})?.data?.fields.map(
                        (field, index) => (
                            <p key={`error-${field.field}-${index}`}>
                                <b>Virhe {index + 1}:</b> {field.message}
                            </p>
                        )
                    )}
                </ErrorSummary>
            )}
            <div className="price-ceiling-calculation">
                {isCurrentQuarterCalculated ? (
                    <CurrentMonthCalculationExists
                        sapcIndexData={sapcIndexData}
                        isCurrentQuarterCalculated={isCurrentQuarterCalculated}
                        handleCalculateButtonOnClick={handleCalculateButtonOnClick}
                        isLoading={isLoading}
                    />
                ) : (
                    <CurrentMonthCalculationMissing
                        isCurrentQuarterCalculated={isCurrentQuarterCalculated}
                        handleCalculateButtonOnClick={handleCalculateButtonOnClick}
                        isLoading={isLoading}
                    />
                )}
                <GenericActionModal
                    title="Rajaneliöhinnan laskenta"
                    modalIcon={<IconCogwheels />}
                    isModalOpen={isModalOpen}
                    closeModal={closeModal}
                    confirmButton={<DownloadSurfaceAreaPriceCeilingResultsButton extraOnClickAction={closeModal} />}
                >
                    <>
                        <p>Rajaneliöhinnan laskenta on suoritettu onnistuneesti.</p>
                        <p>
                            Rajaneliöhinnan laskennan tulos Hitas-vuosineljännelle{" "}
                            {getHitasQuarterFullLabel(currentMonth)} on{" "}
                            <b>{calculationData !== undefined ? calculationData[0].value : "VIRHE"}</b>
                        </p>
                        <p>Haluatko ladata laskentaraportin?</p>
                    </>
                </GenericActionModal>
            </div>
        </>
    );
};

const SurfaceAreaPriceCeilingTab = () => {
    // Get latest 12 SAPC values
    const {
        data: sapcIndexData,
        error,
        isLoading,
    } = useGetIndicesQuery({
        indexType: "surface-area-price-ceiling",
        params: {year: today().split("-")[0], limit: 12, page: 1},
    });

    return (
        <div className="view--functions__surface-area-price-ceiling">
            <Heading type="body">Rajaneliöhinnan laskenta</Heading>
            <QueryStateHandler
                data={sapcIndexData}
                error={error}
                isLoading={isLoading}
                attemptedAction="Haetaan rajaneliöhintalistausta (tarkistetaan onko nykyinen laskettu)"
            >
                <SurfaceAreaPriceCeilingCalculationSection sapcIndexData={sapcIndexData} />
            </QueryStateHandler>

            <Divider size="xl" />

            <Heading type="sub">Vanhat rajaneliöhintalaskelmat</Heading>
            <SurfaceAreaPriceCeilingTable />
        </div>
    );
};

export default SurfaceAreaPriceCeilingTab;
