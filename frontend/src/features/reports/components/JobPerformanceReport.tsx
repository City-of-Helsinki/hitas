import {Table} from "hds-react";
import {Divider, Heading, QueryStateHandler} from "../../../common/components";
import {JobPerformanceResponse} from "../../../common/schemas";
import {
    useGetConfirmedMaximumPriceJobPerformanceQuery,
    useGetUnconfirmedMaximumPriceJobPerformanceQuery,
} from "../../../common/services";
import {tableThemeBlack} from "../../../common/themes";
import {DateInput, FormProviderForm} from "../../../common/components/forms";
import {useForm} from "react-hook-form";
import {format} from "date-fns";
import {getLatestFullMonth} from "../../../common/utils";

const perUserTableColumns = [
    {
        key: "full_name",
        headerName: "Käyttäjä",
    },
    {
        key: "job_performance_count",
        headerName: "Suoritteet",
        transform: (obj) => <div className="text-right">{obj.job_performance_count} kpl</div>,
    },
];

const JobPerformanceDateFields = ({formObject}) => {
    return (
        <FormProviderForm
            formObject={formObject}
            onSubmit={() => {}}
        >
            <div className="date-input-wrap">
                <DateInput
                    name="startDate"
                    label="Alkupäivämäärä"
                    tooltipText="Ensimmäinen päivä, jolta suoritteet lasketaan."
                    maxDate={new Date()}
                    required
                />
                <DateInput
                    name="endDate"
                    label="Loppupäivämäärä"
                    tooltipText="Viimeinen päivä, jolta suoritteet lasketaan."
                    maxDate={new Date()}
                    required
                />
            </div>
        </FormProviderForm>
    );
};

const JobPerformanceDataTable = ({data}: {data: JobPerformanceResponse}) => {
    return (
        <>
            <Table
                cols={perUserTableColumns}
                rows={data.per_user}
                indexKey="full_name"
                theme={tableThemeBlack}
                zebra
            />
            <p className="job-performance-totals">
                <span>
                    <strong>Yhteensä:</strong> {data.totals.count} kpl
                </span>
                |
                <span>
                    <strong>Käsittelyajan keskiarvo:</strong> {data.totals.average_days} päivää
                </span>
                |
                <span>
                    <strong>Pisin käsittelyaika:</strong> {data.totals.maximum_days} päivää
                </span>
            </p>
        </>
    );
};

const JobPerformanceDataContainer = ({header, formObject, queryFunction}) => {
    const watch = formObject.watch();

    const {data, error, isFetching} = queryFunction(
        {
            params: {
                start_date: watch.startDate,
                end_date: watch.endDate,
            },
        },
        {skip: !watch.startDate || !watch.endDate}
    );

    return (
        <>
            <Heading
                type="sub"
                className="job-performance-heading"
            >
                {header}
            </Heading>
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isFetching}
            >
                <JobPerformanceDataTable data={data} />
            </QueryStateHandler>
        </>
    );
};

export const JobPerformanceReport = () => {
    const defaultDates = getLatestFullMonth();
    const formObject = useForm({
        defaultValues: {
            startDate: format(defaultDates.start, "yyyy-MM-dd"),
            endDate: format(defaultDates.end, "yyyy-MM-dd"),
        },
        mode: "all",
    });

    return (
        <div className="report-container">
            <div className="col">
                <JobPerformanceDateFields formObject={formObject} />
                <Divider size="s" />

                <JobPerformanceDataContainer
                    header="Vahvistetut enimmäishintalaskelmat"
                    formObject={formObject}
                    queryFunction={useGetConfirmedMaximumPriceJobPerformanceQuery}
                />
                <Divider size="s" />

                <JobPerformanceDataContainer
                    header="Hinta-arviot"
                    formObject={formObject}
                    queryFunction={useGetUnconfirmedMaximumPriceJobPerformanceQuery}
                />
                <Divider size="s" />
            </div>
        </div>
    );
};
