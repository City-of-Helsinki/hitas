import {Button} from "hds-react";

import {
    downloadSurfaceAreaPriceCeilingResults,
    useCalculatePriceCeilingMutation,
    useGetIndicesQuery,
} from "../../app/services";
import {Heading, QueryStateHandler} from "../../common/components";
import DownloadButton from "../../common/components/DownloadButton";
import PriceCeilingsList from "../../common/components/PriceCeilingsList";
import {getHitasQuarter, hdsToast, today} from "../../common/utils";

export const years = Array.from({length: 34}, (_, index) => {
    const year = 2023 - index;
    return {
        value: year.toString(),
        label: year.toString(),
    };
});

const PriceCeilingCalculationSection = ({data, currentMonth}) => {
    const [calculatePriceCeiling] = useCalculatePriceCeilingMutation();
    const handleCalculateButton = () => {
        calculatePriceCeiling({
            data: {calculation_month: currentMonth},
        })
            .unwrap()
            .then(() => {
                hdsToast.success("Rajahinnan laskenta onnistui");
            })
            .catch((e) => {
                // eslint-disable-next-line no-console
                console.warn(e);
                hdsToast.error("Rajahinnan laskenta epäonnistui");
            });
    };
    const CalculateButton = () => (
        <Button
            className="calculate-button"
            theme="black"
            onClick={handleCalculateButton}
        >
            <span>Laske rajaneliöhinta</span>
        </Button>
    );

    return (
        <div className="price-ceiling-calculation">
            {data.contents.some((item) => item.month === currentMonth) ? (
                <>
                    <div className="price-ceiling-value">
                        <label>
                            Rajaneliöhinta (<>{getHitasQuarter().label}</>)
                        </label>
                        <span>{data.contents[0].value}</span>
                    </div>
                    <DownloadButton
                        onClick={() => downloadSurfaceAreaPriceCeilingResults(currentMonth + "-01")}
                        buttonText="Lataa laskentaraportti"
                    />
                </>
            ) : (
                <>
                    <p>Tälle neljännekselle ({getHitasQuarter().label}) ei vielä ole laskettu rajaneliöhintaa</p>
                    <CalculateButton />
                </>
            )}
        </div>
    );
};

const CalculatePriceCeiling = () => {
    const currentMonth = today().slice(0, 7);
    const {data, error, isLoading} = useGetIndicesQuery({
        indexType: "surface-area-price-ceiling",
        params: {year: today().split("-")[0], limit: 12, page: 1},
    });
    return (
        <div className="view--functions__price-ceiling-per-square">
            <Heading type="body">Rajaneliöhinnan laskenta</Heading>
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
                attemptedAction="Haetaan rajaneliöhintalistausta (tarkistetaan onko nykyinen laskettu)"
            >
                <PriceCeilingCalculationSection
                    data={data}
                    currentMonth={currentMonth}
                />
            </QueryStateHandler>
            <PriceCeilingsList callbackFn={false} />
        </div>
    );
};

export default CalculatePriceCeiling;
