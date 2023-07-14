import React, {useState} from "react";

import {Button, IconPlus, IconSearch, LoadingSpinner, StatusLabel} from "hds-react";
import {Link} from "react-router-dom";

import {useGetDevelopersQuery, useGetHousingCompaniesQuery, useGetPropertyManagersQuery} from "../../app/services";
import {Heading, ListPageNumbers, QueryStateHandler} from "../../common/components";
import {
    FilterIntegerField,
    FilterRelatedModelComboboxField,
    FilterSelectField,
    FilterTextInputField,
} from "../../common/components/filters";
import {getHousingCompanyHitasTypeName} from "../../common/localisation";
import {IHousingCompany, IHousingCompanyListResponse} from "../../common/schemas";
import {formatDate} from "../../common/utils";

const HousingCompanyListItem = ({housingCompany}: {housingCompany: IHousingCompany}): React.JSX.Element => {
    const getStatusLabelText = () => {
        if (housingCompany.regulation_status.startsWith("released")) {
            return "Vapautunut";
        } else if (!housingCompany.completed) {
            return "Ei valmis";
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

const HousingCompanyListPage = (): React.JSX.Element => {
    const [filterParams, setFilterParams] = useState({});

    return (
        <div className="view--housing-company-list">
            <Heading>
                <span>Kaikki kohteet</span>
                <Link to="create">
                    <Button
                        theme="black"
                        iconLeft={<IconPlus />}
                    >
                        Lisää uusi yhtiö
                    </Button>
                </Link>
            </Heading>
            <div className="listing">
                <div className="search">
                    <FilterTextInputField
                        label=""
                        filterFieldName="display_name"
                        filterParams={filterParams}
                        setFilterParams={setFilterParams}
                    />
                    <IconSearch />
                </div>
                <HousingCompanyResultsList filterParams={filterParams} />
                <HousingCompanyFilters
                    filterParams={filterParams}
                    setFilterParams={setFilterParams}
                />
            </div>
        </div>
    );
};

export default HousingCompanyListPage;
