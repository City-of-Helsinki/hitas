import {useParams} from "react-router-dom";

import {createContext} from "react";
import {useGetHousingCompanyDetailQuery} from "../../../app/services";
import {QueryStateHandler} from "../../../common/components";
import {IHousingCompanyDetails} from "../../../common/schemas";

export const HousingCompanyViewContext = createContext<{
    housingCompany?: IHousingCompanyDetails;
}>({
    housingCompany: undefined as unknown as IHousingCompanyDetails | undefined,
});

export const HousingCompanyViewContextProvider = ({
    viewClassName,
    children,
}: {
    viewClassName: string;
    children: React.ReactNode;
}) => {
    const {housingCompanyId}: {housingCompanyId?: string} = useParams();

    // If no housingCompanyId is given, just render the children
    if (!housingCompanyId) return <div className={viewClassName}>{children}</div>;

    const {data, error, isLoading} = useGetHousingCompanyDetailQuery(housingCompanyId as string, {
        skip: !housingCompanyId,
    });

    return (
        <div className={viewClassName}>
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <HousingCompanyViewContext.Provider
                    value={{
                        housingCompany: data as IHousingCompanyDetails | undefined,
                    }}
                >
                    {children}
                </HousingCompanyViewContext.Provider>
            </QueryStateHandler>
        </div>
    );
};
