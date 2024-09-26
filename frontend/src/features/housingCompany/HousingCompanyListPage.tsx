import React, {useState} from "react";

import {Button, IconPlus, IconSearch, LoadingSpinner, StatusLabel} from "hds-react";
import {Link, useNavigate} from "react-router-dom";

import {Heading, ListPageNumbers, QueryStateHandler} from "../../common/components";
import {
    FilterIntegerField,
    FilterRelatedModelComboboxField,
    FilterSelectField,
    FilterTextInputField,
} from "../../common/components/filters";
import {getHousingCompanyHitasTypeName} from "../../common/localisation";
import {IHousingCompany, IHousingCompanyListResponse} from "../../common/schemas";
import {useGetDevelopersQuery, useGetHousingCompaniesQuery, useGetPropertyManagersQuery} from "../../common/services";
import {formatDate} from "../../common/utils";

const HousingCompanyListItem = ({housingCompany}: {housingCompany: IHousingCompany}): React.JSX.Element => {
    const getStatusLabelText = () => {
        if (housingCompany.regulation_status.startsWith("released")) {
            return "Vapautunut";
        } else if (!housingCompany.completed) {
            return `Ei valmis${housingCompany.hitas_type === "rr_new_hitas" ? " (RR)" : ""}`;
        } else {
            return getHousingCompanyHitasTypeName(housingCompany.hitas_type);
        }
    };

    return (
        <Link to={`/housing-companies/${housingCompany.id}`}>
            <li className="results-list__item">
                <div className="name">{housingCompany.name}</div>
                <div className="address">
                    {housingCompany.address.street_address}
                    <br />
                    {housingCompany.address.postal_code}, {housingCompany.address.city}
                </div>
                <div className="date">{formatDate(housingCompany.completion_date)}</div>
                <div className="housing-company-state">
                    <StatusLabel>{getStatusLabelText()}</StatusLabel>
                </div>
            </li>
        </Link>
    );
};

const HousingCompanyResultsList = ({filterParams}): React.JSX.Element => {
    const [currentPage, setCurrentPage] = useState(1);
    const {data, error, isLoading, isFetching} = useGetHousingCompaniesQuery({...filterParams, page: currentPage});

    const LoadedHousingCompanyResultsList = ({
        data,
        isFetching,
    }: {
        data: IHousingCompanyListResponse;
        isFetching: boolean;
    }) => {
        return (
            <>
                <div className="list-headers">
                    <div className="list-header name">Yhtiö</div>
                    <div className="list-header address">Osoite</div>
                    <div className="list-header date">Valmistunut</div>
                    <div className="list-header housing-company-state">Tila</div>
                </div>
                <ul className={`results-list${isFetching ? " results-list-blurred" : ""}`}>
                    {isFetching && (
                        <div className="results-list-overlay-spinner">
                            <LoadingSpinner />
                        </div>
                    )}
                    {data.contents.map((housingCompany: IHousingCompany) => (
                        <HousingCompanyListItem
                            key={housingCompany.id}
                            housingCompany={housingCompany}
                        />
                    ))}
                </ul>
            </>
        );
    };

    return (
        <div className="results">
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <LoadedHousingCompanyResultsList
                    data={data as IHousingCompanyListResponse}
                    isFetching={isFetching}
                />
                <ListPageNumbers
                    currentPage={currentPage}
                    setCurrentPage={setCurrentPage}
                    pageInfo={(data as IHousingCompanyListResponse)?.page}
                />
            </QueryStateHandler>

            {!isLoading ? (
                <div className="list-amount">
                    Haun tulokset: {data?.page.total_items} {data?.page.total_items === 1 ? "yhtiö" : "yhtiötä"}
                </div>
            ) : null}
        </div>
    );
};

const HousingCompanyFilters = ({filterParams, setFilterParams}): React.JSX.Element => {
    return (
        <div className="filters">
            <FilterTextInputField
                label="Osoite"
                filterFieldName="street_address"
                filterParams={filterParams}
                setFilterParams={setFilterParams}
            />
            <FilterIntegerField
                label="Postinumero"
                minLength={5}
                maxLength={5}
                filterFieldName="postal_code"
                filterParams={filterParams}
                setFilterParams={setFilterParams}
            />
            <FilterRelatedModelComboboxField
                label="Rakennuttaja"
                queryFunction={useGetDevelopersQuery}
                labelField="value"
                filterFieldName="developer"
                filterParams={filterParams}
                setFilterParams={setFilterParams}
            />
            <FilterRelatedModelComboboxField
                label="Isännöitsijä"
                queryFunction={useGetPropertyManagersQuery}
                labelField="name"
                filterFieldName="property_manager"
                filterParams={filterParams}
                setFilterParams={setFilterParams}
            />
            <FilterIntegerField
                label="Yhtiön arkistotunnus"
                minLength={1}
                maxLength={10}
                filterFieldName="archive_id"
                filterParams={filterParams}
                setFilterParams={setFilterParams}
            />
            <FilterSelectField
                label="Yhtiön sääntelytila"
                filterFieldName="is_regulated"
                options={[
                    {value: "true", label: "Säännelty"},
                    {value: "false", label: "Ei säännelty"},
                ]}
                filterParams={filterParams}
                setFilterParams={setFilterParams}
            />
        </div>
    );
};

interface FilterParams {
    display_name?: string | undefined;
    street_address?: string | undefined;
    postal_code?: string | undefined;
    developer?: string | undefined;
    property_manager?: string | undefined;
    archive_id?: string | undefined;
    is_regulated?: string | undefined;
}

const getFilterDefaultsFromQueryParams = () => {
    const params = new URLSearchParams(location.search);
    const filterParams: FilterParams = {
        display_name: params.get("display_name") ?? undefined,
        street_address: params.get("street_address") ?? undefined,
        postal_code: params.get("postal_code") ?? undefined,
        developer: params.get("developer") ?? undefined,
        property_manager: params.get("property_manager") ?? undefined,
        archive_id: params.get("archive_id") ?? undefined,
    };
    if (params.get("is_regulated")) {
        filterParams.is_regulated = params.get("is_regulated") ?? undefined;
    }
    return filterParams;
};

const HousingCompanyListPage = (): React.JSX.Element => {
    const navigate = useNavigate();
    const [filterParams, setFilterParams] = useState({
        is_regulated: "true",
        ...getFilterDefaultsFromQueryParams(),
    });

    const updateFilters = (newFilters) => {
        setFilterParams(newFilters);
        // Update URL with new filters
        const queryParams = new URLSearchParams(
            // Remove undefined
            JSON.parse(JSON.stringify(newFilters))
        ).toString();
        navigate(
            {
                pathname: location.pathname,
                search: queryParams,
            },
            {replace: true}
        );
    };

    return (
        <div className="view--housing-company-list">
            <Heading>
                <span>Kaikki kohteet</span>
                <Link to="create">
                    <Button
                        theme="black"
                        iconLeft={<IconPlus />}
                    >
                        Lisää uusi taloyhtiö
                    </Button>
                </Link>
            </Heading>
            <div className="listing">
                <div className="search">
                    <FilterTextInputField
                        label=""
                        filterFieldName="display_name"
                        filterParams={filterParams}
                        setFilterParams={updateFilters}
                    />
                    <IconSearch />
                </div>
                <HousingCompanyResultsList filterParams={filterParams} />
                <HousingCompanyFilters
                    filterParams={filterParams}
                    setFilterParams={updateFilters}
                />
            </div>
        </div>
    );
};

export default HousingCompanyListPage;
