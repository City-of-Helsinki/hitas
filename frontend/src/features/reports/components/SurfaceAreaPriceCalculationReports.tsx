import {Heading, SurfaceAreaPriceCeilingTable} from "../../../common/components";

export const SurfaceAreaPriceCeilingCalculationReport = () => {
    return (
        <div className="report-container surface-area-price-ceiling-report">
            <Heading type="sub">Raportit rajaneliöhintalaskelmista</Heading>
            <SurfaceAreaPriceCeilingTable />
        </div>
    );
};
