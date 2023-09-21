import {useParams} from "react-router-dom";
import {createContext, useEffect, useState} from "react";
import {QueryStateHandler} from "../../../common/components";
import {IApartmentDetails, IHousingCompanyDetails, IOwner} from "../../../common/schemas";
import {
    useGetApartmentDetailQuery,
    useGetHousingCompanyDetailQuery,
    useGetObfuscatedOwnersQuery,
} from "../../../common/services";
import ApartmentHeader from "./ApartmentHeader";
import {skipToken} from "@reduxjs/toolkit/dist/query/react";

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
        isFetching: isApartmentFetching,
        isSuccess: isApartmentSuccess,
    } = useGetApartmentDetailQuery(
        {
            housingCompanyId: params.housingCompanyId,
            apartmentId: params.apartmentId as string,
        },
        {skip: isApartmentMissing}
    );

    const [deObfuscatedApartmentData, setDeObfuscatedApartmentData] = useState<IApartmentDetails | undefined>(
        undefined
    );

    // Check if there are obfuscated owners in the apartmentData
    const [obfuscatedOwnerIds, setObfuscatedOwnerIds] = useState<string[] | undefined>(undefined);
    const [isApartmentDataReady, setIsApartmentDataReady] = useState<boolean>(false);
    useEffect(() => {
        setIsApartmentDataReady(false);
        if (isApartmentSuccess && !isApartmentLoading && !isApartmentFetching) {
            const obfOwnerIds = apartmentData?.ownerships
                .filter((ownership) => ownership.owner.non_disclosure)
                .map((ownership) => ownership.owner.id);
            setObfuscatedOwnerIds(obfOwnerIds);
            setIsApartmentDataReady(true);
            !obfOwnerIds.length && setDeObfuscatedApartmentData(apartmentData);
        }
    }, [isApartmentSuccess, isApartmentLoading, isApartmentFetching, apartmentData]);

    // Fetch obfuscated owner data
    const {
        data: deObfuscatedOwnersData,
        isLoading: isDeObfuscatedOwnersLoading,
        isFetching: isDeobfuscatedOwnersFetching,
        isSuccess: isDeObfuscatedOwnersSuccess,
    } = useGetObfuscatedOwnersQuery(
        isApartmentDataReady && obfuscatedOwnerIds?.length ? obfuscatedOwnerIds : skipToken
    );

    // Create deobfuscated apartment data
    useEffect(() => {
        if (
            isApartmentDataReady &&
            obfuscatedOwnerIds?.length &&
            isDeObfuscatedOwnersSuccess &&
            !isDeObfuscatedOwnersLoading &&
            !isDeobfuscatedOwnersFetching &&
            deObfuscatedOwnersData?.data.length
        ) {
            const deObfuscatedApartmentDataObject = {
                ...apartmentData,
                ownerships: apartmentData?.ownerships.map((ownership) => {
                    const obfOwner = deObfuscatedOwnersData?.data.find(
                        (deObfuscatedOwner) => (deObfuscatedOwner as IOwner).id === ownership.owner.id
                    );
                    if (obfOwner) {
                        const newOwnership = {...ownership};
                        newOwnership.owner = obfOwner as IOwner;
                        return newOwnership;
                    }
                    return ownership;
                }),
            };
            setDeObfuscatedApartmentData(deObfuscatedApartmentDataObject as IApartmentDetails);
        }
    }, [
        isApartmentDataReady,
        obfuscatedOwnerIds?.length,
        isDeObfuscatedOwnersSuccess,
        isDeObfuscatedOwnersLoading,
        isDeobfuscatedOwnersFetching,
        deObfuscatedOwnersData?.data.length,
    ]);

    // Get error from deObfuscatedOwnersData
    const deObfuscatedOwnerError = () => {
        if (deObfuscatedOwnersData?.error && deObfuscatedOwnersData.error.length) {
            return deObfuscatedOwnersData?.error[0];
        }
        return undefined;
    };

    const data = isApartmentMissing ? housingCompanyData : housingCompanyData && deObfuscatedApartmentData;
    const error = housingCompanyError || apartmentError || deObfuscatedOwnerError();
    const isLoading = isHousingCompanyLoading || (!isApartmentMissing && isApartmentLoading);

    if (!deObfuscatedApartmentData && !isApartmentMissing) {
        return <></>;
    }
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
                        apartment: deObfuscatedApartmentData as IApartmentDetails | undefined,
                    }}
                >
                    {children}
                </ApartmentViewContext.Provider>
            </QueryStateHandler>
        </div>
    );
};
