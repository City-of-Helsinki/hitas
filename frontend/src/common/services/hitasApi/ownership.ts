import {IOwnership, IOwnershipUpdate} from "../../schemas";
import {safeInvalidate} from "../utils";
import {hitasApi} from "../apis";

const ownershipApi = hitasApi.injectEndpoints({
    endpoints: (builder) => ({
        updateOwnership: builder.mutation<
            IOwnership,
            {ownershipId: string; apartmentId: string; data: IOwnershipUpdate}
        >({
            query: ({ownershipId, data}) => ({
                url: `ownerships/${ownershipId}`,
                method: "PATCH",
                body: data,
            }),
            invalidatesTags: (result, error, {apartmentId}) =>
                safeInvalidate(error, [{type: "Apartment", id: apartmentId}]),
        }),
    }),
});

export const {useUpdateOwnershipMutation} = ownershipApi;
