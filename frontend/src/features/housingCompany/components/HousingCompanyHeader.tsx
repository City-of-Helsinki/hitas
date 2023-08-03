import {StatusLabel} from "hds-react";
import {Link, useLocation, useParams} from "react-router-dom";

import {EditButton, Heading, QueryStateHandler} from "../../../common/components";
import {getHousingCompanyHitasTypeName, getHousingCompanyRegulationStatusName} from "../../../common/localisation";
import {IHousingCompanyDetails} from "../../../common/schemas";
import {useGetHousingCompanyDetailQuery} from "../../../common/services";

const HousingCompanyHeaderContent = ({housingCompany}: {housingCompany: IHousingCompanyDetails}) => {
    const {pathname} = useLocation();
    const isHousingCompanySubPage = pathname.split("/").pop() !== housingCompany.id;

    // Edit button is visible only if the housing company is regulated and user is on the housing company main page
    const isEditButtonVisible = housingCompany.regulation_status === "regulated" && !isHousingCompanySubPage;

    return (
        <>
            <div>
                {isHousingCompanySubPage ? (
                    <Link to={`/housing-companies/${housingCompany.id}`}>
                        <Heading type="main">{housingCompany.name.display}</Heading>
                    </Link>
                ) : (
                    <Heading type="main">
                        {housingCompany.name.display}
                        {isEditButtonVisible ? <EditButton /> : null}
                    </Heading>
                )}
            </div>
            <div>
                <StatusLabel>{getHousingCompanyHitasTypeName(housingCompany.hitas_type)}</StatusLabel>
                <StatusLabel>{housingCompany.completed ? "Valmis" : "Ei valmis"}</StatusLabel>

                {housingCompany.completed ? (
                    <>
                        {housingCompany.hitas_type !== "half_hitas" ? (
                            <StatusLabel>
                                {housingCompany.over_thirty_years_old ? "Yli 30 vuotta" : "Alle 30 vuotta"}
                            </StatusLabel>
                        ) : null}
                        <StatusLabel>
                            {getHousingCompanyRegulationStatusName(housingCompany.regulation_status)}
                        </StatusLabel>
                    </>
                ) : null}

                {housingCompany.hitas_type === "rr_new_hitas" && <StatusLabel>Ryhmärakentamiskohde</StatusLabel>}

                {housingCompany.exclude_from_statistics ? <StatusLabel>Ei tilastoihin</StatusLabel> : null}
            </div>
        </>
    );
};

const HousingCompanyHeader = () => {
    const {housingCompanyId}: {housingCompanyId?: string} = useParams();

    const {data, error, isLoading} = useGetHousingCompanyDetailQuery(housingCompanyId as string, {
        skip: !housingCompanyId,
    });

    if (!housingCompanyId) {
        return <Heading>Uusi taloyhtiö</Heading>;
    }

    return (
        <div className="housing-company-header">
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <HousingCompanyHeaderContent housingCompany={data as IHousingCompanyDetails} />
            </QueryStateHandler>
        </div>
    );
};

export default HousingCompanyHeader;
