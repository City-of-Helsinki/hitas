import {Divider, DownloadButton, Heading} from "../../../common/components";
import {downloadHousingCompanyWithOwnersExcel, downloadMultipleOwnershipsReportPDF} from "../../../common/services";
import React from "react";

/* Jos laitetaan tiedot taulukkoon myös
const ownersByHousingCompanyColumns = [
    {
        key: "number",
        headerName: "Asunnon nro",
    },
    {
        key: "surface_area",
        headerName: "Asunnon pinta-ala",
    },
    {
        key: "share_numbers",
        headerName: "Osakenumerot",
    },
    {
        key: "purchase_date",
        headerName: "Kauppakirjapäivä",
    },
    {
        key: "owner_name",
        headerName: "Omistajan nimi",
    },
    {
        key: "owner_ssn",
        headerName: "Henkilötunnus",
    },
];

*/
const OwnerReports = () => {
    // const [filterParams, setFilterParams] = useState({is_regulated: "false", page: "1"});
    // const {data, error, isLoading, isFetching} = useGetHousingCompaniesQuery({...filterParams, page: 1});
    // console.log(data, error, isLoading, isFetching);

    return (
        <div className="report-container">
            <div className="column">
                <Heading type="sub">Usean Hitas-asunnon omistajat</Heading>
                <span>
                    Listaus henkilöistä, jotka omistavat useamman kuin yhden Hitas-asunnon, sekä heidän omistuksistaan.
                </span>
                <div>
                    <DownloadButton
                        buttonText="Lataa raportti"
                        onClick={downloadMultipleOwnershipsReportPDF}
                    />
                </div>
            </div>
            <Divider size="s" />

            <Heading type="sub">Omistajat yhtiöittäin</Heading>

            <DownloadButton
                buttonText="Lataa raportti"
                onClick={downloadHousingCompanyWithOwnersExcel}
            />
        </div>
    );
};
/*
TODOI QueryStateHandler Tablelle ja Download buttonin ympärille
Oikea download ekkeli hookki oikeeta data
 */

export default OwnerReports;
