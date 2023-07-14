import {
    downloadHousingCompanyStatesReportPDF,
    downloadRegulatedHousingCompaniesPDF,
    downloadUnregulatedHousingCompaniesPDF,
    useGetHousingCompanyStatesQuery,
} from "../../../app/services";
import {QueryStateHandler} from "../../../common/components";
import DownloadButton from "../../../common/components/DownloadButton";
import {IHousingCompanyState} from "../../../common/schemas";

const LoadedHousingCompanyStatusTable = ({housingCompanyStates}) => {
    return (
        <>
            <ul className="state-list">
                <li className="state-list-headers">
                    <span>Tila</span>
                    <div className="state-values">
                        <span>Yhtiöitä</span>
                        <span>Asuntoja</span>
                    </div>
                </li>
                {housingCompanyStates.map((state: IHousingCompanyState) => (
                    <li key={state.status}>
                        <span>{state.status}</span>
                        <div className="state-values">
                            <span>{state.housing_company_count}</span>
                            <span>{state.apartment_count}</span>
                        </div>
                    </li>
                ))}
            </ul>
            <div className="row row--buttons">
                <DownloadButton
                    buttonText="Lataa lukumäärät tiloittain"
                    onClick={downloadHousingCompanyStatesReportPDF}
                />
            </div>
        </>
    );
};

export const HousingCompanyStatusTable = () => {
    const {data, error, isLoading} = useGetHousingCompanyStatesQuery({});

    return (
        <div className="report-container">
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <LoadedHousingCompanyStatusTable housingCompanyStates={data as IHousingCompanyState[]} />
            </QueryStateHandler>
        </div>
    );
};

export const HousingCompanyReportRegulated = () => {
    return (
        <div className="report-container">
            <p>Listaus säännellyistä taloyhtiöistä.</p>
            <DownloadButton
                buttonText="Lataa säännellyt yhtiöt"
                onClick={downloadRegulatedHousingCompaniesPDF}
            />
        </div>
    );
};

export const HousingCompanyReportReleased = () => {
    return (
        <div className="report-container">
            <p>Listaus sääntelystä vapautuneista taloyhtiöistä.</p>
            <DownloadButton
                buttonText="Lataa vapautuneet yhtiöt"
                onClick={downloadUnregulatedHousingCompaniesPDF}
            />
        </div>
    );
};
