import {Button} from "hds-react";
import {useFieldArray, useForm} from "react-hook-form";
import {useGetAvailablePostalCodesQuery} from "../../../app/services";
import {Heading, QueryStateHandler} from "../../../common/components";
import {today} from "../../../common/utils";
import ComparisonSkippedListItem from "./ComparisonSkippedListItem";

type NewPostalCodes = {
    skipped: {
        postalCode1: string | null;
        postalCode2: string | null;
    }[];
};

const ComparisonSkippedList = ({companies, calculationDate, reCalculateFn}) => {
    // If in Test mode, use today's date as the calculation date
    const validCalculationDate = isNaN(Number(calculationDate.substring(0, 4))) ? today() : calculationDate;
    const {
        data: codes,
        error,
        isLoading,
    } = useGetAvailablePostalCodesQuery({
        calculation_date: validCalculationDate,
    });

    const skippedPostalCodes = {};
    // If there are skipped companies, group them by postal code
    if (companies && companies.length > 0) {
        companies.forEach(
            (company) =>
                (skippedPostalCodes[company.address.postal_code] =
                    skippedPostalCodes[company.address.postal_code] !== undefined
                        ? [...skippedPostalCodes[company.address.postal_code], company]
                        : [company])
        );
        // console.log("skipped:", skippedPostalCodes);
    }
    const initialValues: object[] = [];
    Object.entries(skippedPostalCodes).map((code) => initialValues.push({postalCode1: null, postalCode2: null}));
    const skippedForm = useForm<NewPostalCodes>({
        defaultValues: {skipped: initialValues},
        mode: "onBlur",
    });
    const {control} = skippedForm;
    const {fields} = useFieldArray({name: "skipped", control});

    const onSubmit = (data) => {
        console.log(data);
    };
    return (
        <form
            className="companies companies--skipped"
            onSubmit={skippedForm.handleSubmit(onSubmit)}
        >
            <Heading type="body">Vertailua ei voitu suorittaa</Heading>
            <h3 className="error-text">
                Seuraavilta postinumeroalueilta puuttuu keskineliöhinta, ole hyvä ja valitse korvaavat postinumeroalueet
            </h3>
            <QueryStateHandler
                data={codes}
                error={error}
                isLoading={isLoading}
            >
                <div className="list">
                    <ul className="results-list">
                        {Object.entries(skippedPostalCodes).map(([key, value], index) => (
                            <ComparisonSkippedListItem
                                key={key}
                                postalCode={key}
                                companies={value}
                                postalCodeOptionSet={codes}
                                formObject={skippedForm}
                                index={index}
                            />
                        ))}
                    </ul>
                </div>
            </QueryStateHandler>
            <div className="row row--buttons">
                {/* TODO: Add disabling of button if form is invalid */}
                <Button
                    theme="black"
                    type="submit"
                    onClick={() => reCalculateFn(fields)}
                >
                    Suorita vertailu korvaavin postinumeroin
                </Button>
            </div>
        </form>
    );
};

export default ComparisonSkippedList;
