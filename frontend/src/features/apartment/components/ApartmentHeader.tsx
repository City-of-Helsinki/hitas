import {IconLock, StatusLabel} from "hds-react";
import {Link, useLocation, useParams} from "react-router-dom";

import {EditButton, Heading, QueryStateHandler} from "../../../common/components";
import {getApartmentSoldStatusLabel, getHousingCompanyRegulationStatusName} from "../../../common/localisation";
import {IApartmentDetails, IHousingCompanyDetails} from "../../../common/schemas";
import {useGetApartmentDetailQuery, useGetHousingCompanyDetailQuery} from "../../../common/services";
import {formatAddress} from "../../../common/utils";

const ApartmentHeaderContent = ({
    apartment,
    housingCompany,
}: {
    apartment: IApartmentDetails;
    housingCompany: IHousingCompanyDetails;
}) => {
    const {pathname} = useLocation();
    const isApartmentSubPage = pathname.split("/").pop() !== apartment.id;

    return (
        <div>
            <Link to={`/housing-companies/${apartment.links.housing_company.id}`}>
                <span className="name">
                    {apartment.links.housing_company.display_name} {isApartmentSubPage}
                </span>
            </Link>

            <span className="unselectable">|</span>

            {isApartmentSubPage ? (
                <Link to={`/housing-companies/${apartment.links.housing_company.id}/apartments/${apartment.id}`}>
                    <span className="address">{apartment && formatAddress(apartment.address)}</span>
                </Link>
            ) : (
                <span className="address">{apartment && formatAddress(apartment.address)}</span>
            )}

            <StatusLabel>{getApartmentSoldStatusLabel(apartment)}</StatusLabel>

            {housingCompany.regulation_status !== "regulated" && (
                <StatusLabel>{getHousingCompanyRegulationStatusName(housingCompany.regulation_status)}</StatusLabel>
            )}
            {!housingCompany.completed && <StatusLabel>Taloyhtiö ei valmis</StatusLabel>}

            {apartment.sell_by_date && (
                <StatusLabel
                    className="conditions-of-sale-status"
                    iconLeft={<IconLock />}
                />
            )}
        </div>
    );
};

const ApartmentHeader = () => {
    const params = useParams() as {housingCompanyId: string; apartmentId: string};

    if (!params.apartmentId) {
        return <Heading>Uusi asunto</Heading>;
    }

    const {
        data: housingCompanyData,
        error: housingCompanyError,
        isLoading: isHousingCompanyLoading,
    } = useGetHousingCompanyDetailQuery(params.housingCompanyId);
    const {
        data: apartmentData,
        error: apartmentError,
        isLoading: isApartmentLoading,
    } = useGetApartmentDetailQuery({
        housingCompanyId: params.housingCompanyId,
        apartmentId: params.apartmentId,
    });

    const {pathname} = useLocation();
    const isApartmentSubPage = pathname.split("/").pop() !== params.apartmentId;

    // Edit button is visible only if the housing company is regulated and user is on the apartment main page
    const isEditButtonVisible = housingCompanyData?.regulation_status === "regulated" && !isApartmentSubPage;

    return (
        <Heading
            type="main"
            className="heading--apartment"
        >
            <QueryStateHandler
                data={housingCompanyData && apartmentData}
                error={housingCompanyError || apartmentError}
                isLoading={isHousingCompanyLoading || isApartmentLoading}
            >
                <ApartmentHeaderContent
                    apartment={apartmentData as IApartmentDetails}
                    housingCompany={housingCompanyData as IHousingCompanyDetails}
                />
            </QueryStateHandler>
            {isEditButtonVisible ? <EditButton /> : null}
        </Heading>
    );
};

export default ApartmentHeader;
