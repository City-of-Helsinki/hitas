import {Button, IconCogwheels} from "hds-react";

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

const CalculateSurfaceAreaPriceCeilingButton = ({handleCalculateButtonOnClick, isLoading}) => {
    return (
        <Button
            theme="black"
            onClick={handleCalculateButtonOnClick}
            iconLeft={<IconCogwheels />}
            isLoading={isLoading}
        >
            Laske rajaneliöhinta
        </Button>
    );
};

const CurrentMonthCalculationExists = ({sapcIndexData}) => {
    const currentMonth = today().slice(0, 7);

    return (
        <>
            <div className="price-ceiling-value">
                <label>Rajaneliöhinta {getHitasQuarterFullLabel(currentMonth)}</label>
                <span>{sapcIndexData.contents[0].value}</span>
            </div>
            <DownloadSurfaceAreaPriceCeilingResultsButton />
        </>
    );
};

const CurrentMonthCalculationMissing = ({handleCalculateButtonOnClick, isLoading}) => {
    const currentMonth = today().slice(0, 7);

    return (
        <>
            <p>
                Tälle Hitas-neljännekselle <b>{getHitasQuarterFullLabel(currentMonth)}</b> ei vielä ole laskettu
                rajaneliöhintaa.
            </p>
            <CalculateSurfaceAreaPriceCeilingButton
                handleCalculateButtonOnClick={handleCalculateButtonOnClick}
                isLoading={isLoading}
            />
        </>
    );
};

const SurfaceAreaPriceCeilingCalculationSection = ({sapcIndexData}) => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const closeModal = () => setIsModalOpen(false);

    const [calculatePriceCeiling, {data: calculationData, isLoading}] = useCalculatePriceCeilingMutation();

    const handleCalculateButtonOnClick = () => {
        calculatePriceCeiling({
            data: {calculation_month: currentMonth},
        })
            .unwrap()
            .then(() => {
                hdsToast.success("Rajahinnan laskenta onnistui");
                setIsModalOpen(true);
            })
            .catch((e) => {
                hdsToast.error("Rajahinnan laskenta epäonnistui");
                // eslint-disable-next-line no-console
                console.error(e);
            });
    };

    const currentMonth = today().slice(0, 7);

    // Check if SAPC for current month is already calculated
    const isCurrentQuarterCalculated = sapcIndexData.contents.some((item) => item.month === currentMonth);

    return (
        <div className="price-ceiling-calculation">
            {isCurrentQuarterCalculated ? (
                <CurrentMonthCalculationExists sapcIndexData={sapcIndexData} />
            ) : (
                <CurrentMonthCalculationMissing
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
                        Rajaneliöhinnan laskennan tulos Hitas-vuosineljännelle {getHitasQuarterFullLabel(currentMonth)}{" "}
                        on <b>{calculationData !== undefined ? calculationData[0].value : "VIRHE"}</b>
                    </p>
                    <p>Haluatko ladata laskentaraportin?</p>
                </>
            </GenericActionModal>
        </div>
    );
};

const sapcTableColumns = [
    {
        key: "period",
        headerName: "Hitas-vuosineljännes",
        transform: (obj) => <div className="text-right">{obj.period}</div>,
    },
    {
        key: "value",
        headerName: "Rajaneliöhinta (€/m²)",
        transform: (obj) => <div className="text-right">{obj.value}</div>,
    },
];

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
            <SurfaceAreaPriceCeilingTable
                tableColumns={sapcTableColumns}
                helpText=""
            />
        </div>
    );
};

export default SurfaceAreaPriceCeilingTab;
