import {Accordion} from "hds-react";
import {QueryStateHandler} from "../../common/components";
import {useGetPDFBodiesQuery} from "../../common/services";
import PDFTemplate from "./components/PDFTemplate";

const ManagePDFTemplates = () => {
    const {data, error, isLoading} = useGetPDFBodiesQuery({});
    return (
        <div>
            <Accordion heading="Enimmäishintalaskelma">
                <QueryStateHandler
                    data={data}
                    error={error}
                    isLoading={isLoading}
                >
                    <PDFTemplate
                        data={data}
                        type="unconfirmed_max_price_calculation"
                    />
                </QueryStateHandler>
            </Accordion>
            <Accordion heading="Vahvistettu enimmäishintalaskelma">
                <QueryStateHandler
                    data={data}
                    error={error}
                    isLoading={isLoading}
                >
                    <PDFTemplate
                        data={data}
                        type="confirmed_max_price_calculation"
                    />
                </QueryStateHandler>
            </Accordion>
            <Accordion heading="Vapautuva yhtiö">
                <QueryStateHandler
                    data={data}
                    error={error}
                    isLoading={isLoading}
                >
                    <PDFTemplate
                        data={data}
                        type="released_from_regulation"
                    />
                </QueryStateHandler>
            </Accordion>
            <Accordion heading="Valvonnan piiriin jäävä yhtiö">
                <QueryStateHandler
                    data={data}
                    error={error}
                    isLoading={isLoading}
                >
                    <PDFTemplate
                        data={data}
                        type="stays_regulated"
                    />
                </QueryStateHandler>
            </Accordion>
        </div>
    );
};

export default ManagePDFTemplates;
