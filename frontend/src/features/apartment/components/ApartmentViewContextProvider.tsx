import {useParams} from "react-router-dom";

import {createContext} from "react";
import {useGetApartmentDetailQuery, useGetHousingCompanyDetailQuery} from "../../../app/services";
import {QueryStateHandler} from "../../../common/components";
import {IApartmentDetails, IHousingCompanyDetails} from "../../../common/schemas";
import ApartmentHeader from "./ApartmentHeader";

export const ApartmentViewContext = createContext<{
    housingCompany: IHousingCompanyDetails;
    apartment?: IApartmentDetails;
}>({
    housingCompany: undefined as unknown as IHousingCompanyDetails,
    apartment: undefined as unknown as IApartmentDetails | undefined,
});

export const ApartmentViewContextProvider = ({
    viewClassName,
    children,
}: {
    viewClassName: string;
    children: React.ReactNode;
}) => {
    const params = useParams() as {housingCompanyId: string; apartmentId?: string};
    const isApartmentMissing = !params.apartmentId;

    const {
        data: housingCompanyData,
        error: housingCompanyError,
        isLoading: isHousingCompanyLoading,
    } = useGetHousingCompanyDetailQuery(params.housingCompanyId);
    const {
        data: apartmentData,
        error: apartmentError,
        isLoading: isApartmentLoading,
    } = useGetApartmentDetailQuery(
        {
            housingCompanyId: params.housingCompanyId,
            apartmentId: params.apartmentId as string,
        },
        {skip: isApartmentMissing}
    );

    const data = isApartmentMissing ? housingCompanyData : housingCompanyData && apartmentData;
    const error = housingCompanyError || apartmentError;
    const isLoading = isHousingCompanyLoading || (!isApartmentMissing && isApartmentLoading);

    return (
        <div className={viewClassName}>
            <ApartmentHeader />
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <ApartmentViewContext.Provider
                    value={{
                        housingCompany: housingCompanyData as IHousingCompanyDetails,
                        apartment: apartmentData as IApartmentDetails | undefined,
                    }}
                >
                    {children}
                </ApartmentViewContext.Provider>
            </QueryStateHandler>
        </div>
    );
};
