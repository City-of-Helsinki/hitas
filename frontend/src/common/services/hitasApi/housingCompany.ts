import {
    IApartmentListResponse,
    IBuilding,
    IBuildingWritable,
    ICodeResponse,
    IHousingCompanyApartmentQuery,
    IHousingCompanyDetails,
    IHousingCompanyListResponse,
    IHousingCompanyWritable,
    IRealEstate,
} from "../../schemas";
import {idOrBlank, mutationApiExcelHeaders, safeInvalidate} from "../utils";

import {hitasApi} from "../apis";

const housingCompanyApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        // FETCH
        getHousingCompanies: builder.query<IHousingCompanyListResponse, object>({
            query: (params: object) => ({
                url: "housing-companies",
                params: params,
            }),
            providesTags: [{type: "HousingCompany", id: "LIST"}],
        }),
        getHousingCompanyDetail: builder.query<IHousingCompanyDetails, string>({
            query: (id) => `housing-companies/${id}`,
            providesTags: (result, error, arg) => [
                {type: "HousingCompany", id: arg},
                {type: "PropertyManager", id: result?.property_manager?.id},
                {type: "Developer", id: result?.developer?.id},
            ],
        }),
        // MODIFY
        saveHousingCompany: builder.mutation<IHousingCompanyDetails, {data: IHousingCompanyWritable; id?: string}>({
            query: ({data, id}) => ({
                url: `housing-companies${idOrBlank(id)}`,
                method: id === undefined ? "POST" : "PUT",
                body: data,
            }),
            invalidatesTags: (result, error, arg) =>
                safeInvalidate(error, [
                    {type: "HousingCompany", id: "LIST"},
                    {type: "HousingCompany", id: arg.id},
                    {type: "Apartment"},
                ]),
        }),
        patchHousingCompany: builder.mutation<
            IHousingCompanyDetails,
            {id: string; data: Partial<IHousingCompanyWritable>}
        >({
            query: ({id, data}) => ({
                url: `housing-companies/${id}`,
                method: "PATCH",
                body: data,
            }),
            invalidatesTags: (result, error, arg) =>
                safeInvalidate(error, [
                    {type: "HousingCompany", id: "LIST"},
                    {type: "HousingCompany", id: arg.id},
                    {type: "Apartment"},
                ]),
        }),
        releaseHousingCompanyFromRegulation: builder.mutation<
            IHousingCompanyDetails,
            {housingCompanyId: string; calculationDate: string}
        >({
            query: ({housingCompanyId}) => ({
                url: `housing-companies/${housingCompanyId}`,
                method: "PATCH",
                body: {regulation_status: "released_by_plot_department"},
            }),
            invalidatesTags: (result, error) => safeInvalidate(error, [{type: "HousingCompany"}, {type: "Apartment"}]),
        }),
        // Real Estate
        saveRealEstate: builder.mutation<IRealEstate, {data: IRealEstate; housingCompanyId: string}>({
            query: ({data, housingCompanyId}) => ({
                url: `housing-companies/${housingCompanyId}/real-estates${idOrBlank(data.id)}`,
                method: data.id === undefined ? "POST" : "PUT",
                body: data,
            }),
            invalidatesTags: (result, error, arg) =>
                safeInvalidate(error, [{type: "HousingCompany", id: arg.housingCompanyId}]),
        }),
        deleteRealEstate: builder.mutation<IRealEstate, {id: string; housingCompanyId: string}>({
            query: ({id, housingCompanyId}) => ({
                url: `housing-companies/${housingCompanyId}/real-estates/${id}`,
                method: "DELETE",
            }),
            invalidatesTags: (result, error, arg) =>
                safeInvalidate(error, [{type: "HousingCompany", id: arg.housingCompanyId}]),
        }),
        // Building
        saveBuilding: builder.mutation<
            IBuilding,
            {data: IBuildingWritable; housingCompanyId: string; realEstateId: string}
        >({
            query: ({data, housingCompanyId, realEstateId}) => ({
                url: `housing-companies/${housingCompanyId}/real-estates/${realEstateId}/buildings${idOrBlank(
                    data.id
                )}`,
                method: data.id === undefined ? "POST" : "PUT",
                body: data,
            }),
            invalidatesTags: (result, error, arg) =>
                safeInvalidate(error, [{type: "HousingCompany", id: arg.housingCompanyId}, {type: "Apartment"}]),
        }),
        deleteBuilding: builder.mutation<IBuilding, {id: string; housingCompanyId: string; realEstateId: string}>({
            query: ({id, housingCompanyId, realEstateId}) => ({
                url: `housing-companies/${housingCompanyId}/real-estates/${realEstateId}/buildings/${id}`,
                method: "DELETE",
            }),
            invalidatesTags: (result, error, arg) =>
                safeInvalidate(error, [{type: "HousingCompany", id: arg.housingCompanyId}]),
        }),
        // Sales Catalog
        validateSalesCatalog: builder.mutation({
            query: ({data, housingCompanyId}) => ({
                url: `housing-companies/${housingCompanyId}/sales-catalog-validate`,
                method: "POST",
                body: data,
                headers: mutationApiExcelHeaders(),
            }),
        }),
        createFromSalesCatalog: builder.mutation({
            query: ({data, housingCompanyId}) => ({
                url: `housing-companies/${housingCompanyId}/sales-catalog-create`,
                method: "POST",
                body: data,
            }),
            invalidatesTags: (result, error) => safeInvalidate(error, [{type: "HousingCompany"}, {type: "Apartment"}]),
        }),
        // Apartment
        getHousingCompanyApartments: builder.query<IApartmentListResponse, IHousingCompanyApartmentQuery>({
            query: (params: IHousingCompanyApartmentQuery) => ({
                url: `housing-companies/${params.housingCompanyId}/apartments`,
                params: params.params,
            }),
            providesTags: (result, error, arg) => [
                {type: "HousingCompany", id: arg.housingCompanyId},
                {type: "Apartment", id: "LIST"},
            ],
        }),
        batchCompleteApartments: builder.mutation({
            query: (arg) => ({
                url: `housing-companies/${arg.housing_company_id}/batch-complete-apartments`,
                method: "PATCH",
                body: arg.data,
            }),
            invalidatesTags: (result, error) => safeInvalidate(error, [{type: "Apartment"}]),
        }),

        getBuildingTypes: builder.query<ICodeResponse, object>({
            query: (params: object) => ({
                url: "building-types",
                params: params,
            }),
        }),
    }),
});

export const {
    useBatchCompleteApartmentsMutation,
    useCreateFromSalesCatalogMutation,
    useDeleteBuildingMutation,
    useDeleteRealEstateMutation,
    useGetBuildingTypesQuery,
    useGetHousingCompaniesQuery,
    useGetHousingCompanyApartmentsQuery,
    useGetHousingCompanyDetailQuery,
    usePatchHousingCompanyMutation,
    useReleaseHousingCompanyFromRegulationMutation,
    useSaveBuildingMutation,
    useSaveHousingCompanyMutation,
    useSaveRealEstateMutation,
    useValidateSalesCatalogMutation,
} = housingCompanyApi;
