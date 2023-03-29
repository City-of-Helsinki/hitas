import {useParams} from "react-router-dom";
import {useGetApartmentDetailQuery} from "../../../app/services";
import {QueryStateHandler} from "../../../common/components";
import {IApartmentDetails} from "../../../common/schemas";
import {MaximumPriceCalculationLoader} from "./MaximumPriceCalculationLoader";

const ApartmentNewSalePage = () => {
    const params = useParams();
    const {data, error, isLoading} = useGetApartmentDetailQuery({
        housingCompanyId: params.housingCompanyId as string,
        apartmentId: params.apartmentId as string,
    });

    return (
        <div className="view--apartment-sales">
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <MaximumPriceCalculationLoader apartment={data as IApartmentDetails} />
            </QueryStateHandler>
        </div>
    );
};

export default ApartmentNewSalePage;
