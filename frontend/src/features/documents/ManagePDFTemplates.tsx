import {Accordion} from "hds-react";
import {useGetPDFBodiesQuery} from "../../app/services";
import {QueryStateHandler} from "../../common/components";
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
            <Accordion heading="Vapautuva yhtiö" />
            <Accordion heading="Valvonnan piiriin jäävä yhtiö" />
        </div>
    );
};

export default ManagePDFTemplates;
