import {useForm} from "react-hook-form";
import {
    downloadHousingCompanyStatesReportPDF,
    downloadRegulatedHousingCompaniesPDF,
    downloadUnregulatedHousingCompaniesPDF,
    useGetHousingCompanyStatesQuery,
} from "../../app/services";
import {Divider, QueryStateHandler} from "../../common/components";
import DownloadButton from "../../common/components/DownloadButton";
import {IHousingCompanyState} from "../../common/schemas";

const HousingCompanyReports = () => {
    const {handleSubmit} = useForm();
    const {data, error, isLoading} = useGetHousingCompanyStatesQuery({});
    return (
        <>
            <Divider size="s" />
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                {data && (
                    <form onSubmit={handleSubmit(downloadHousingCompanyStatesReportPDF)}>
                        <ul className="state-list">
                            <li className="state-list-headers">
                                <span>Tila</span>
                                <div className="state-values">
                                    <span>Yhtiöitä</span>
                                    <span>Asuntoja</span>
                                </div>
                            </li>
                            {(data as IHousingCompanyState[]).map((state: IHousingCompanyState) => (
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
                                type="submit"
                            />
                        </div>
                    </form>
                )}
            </QueryStateHandler>
            <Divider size="s" />
            <form onSubmit={handleSubmit(downloadRegulatedHousingCompaniesPDF)}>
                <p>Listaus säännellyistä taloyhtiöistä.</p>
                <DownloadButton
                    buttonText="Lataa säännellyt yhtiöt"
                    type="submit"
                />
            </form>
            <Divider size="s" />
            <form onSubmit={handleSubmit(downloadUnregulatedHousingCompaniesPDF)}>
                <p>Listaus sääntelystä vapautuneistataloyhtiöistä.</p>
                <DownloadButton
                    buttonText="Lataa vapautuneet yhtiöt"
                    type="submit"
                />
            </form>
        </>
    );
};

export default HousingCompanyReports;
