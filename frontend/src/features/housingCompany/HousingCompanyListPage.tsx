import React, {useState} from "react";

import {Button, SearchInput} from "hds-react";
import {Link} from "react-router-dom";

import {useGetDevelopersQuery, useGetHousingCompaniesQuery, useGetPropertyManagersQuery} from "../../app/services";
import {FilterPostalCodeInput, FilterTextInput, ListPageNumbers, QueryStateHandler} from "../../common/components";
import RelatedModelFilterCombobox from "../../common/components/RelatedModelFilterCombobox";
import {IHousingCompany, IHousingCompanyListResponse} from "../../common/models";
import {formatAddress} from "../../common/utils";

const HousingCompanyListItem = ({id, name, address, date}) => {
    return (
        <Link to={`/housing-companies/${id}`}>
            <li className="results-list__item">
                <div className="name">{name}</div>
                <div className="address">{formatAddress(address)}</div>
                <div className="date">{date}</div>
            </li>
        </Link>
    );
};

const HousingCompanyResultsList = ({filterParams}) => {
    const [currentPage, setCurrentPage] = useState(1);
    const {data, error, isLoading} = useGetHousingCompaniesQuery({...filterParams, page: currentPage});

    const LoadedHousingCompanyResultsList = ({data}: {data: IHousingCompanyListResponse}) => {
        return (
            <>
                <div>Rekisterin tulokset: {data.page.total_items} yhtiötä</div>
                <div className="list-headers">
                    <div className="list-header name">Yhtiö</div>
                    <div className="list-header address">Osoite</div>
                    <div className="list-header date">Valmiustila, pvm</div>
                </div>
                <ul className="results-list">
                    {data.contents.map((item: IHousingCompany) => (
                        <HousingCompanyListItem
                            key={item.id}
                            id={item.id}
                            name={item.name}
                            address={item.address}
                            date={item.date}
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
                <LoadedHousingCompanyResultsList data={data as IHousingCompanyListResponse} />
                <ListPageNumbers
                    currentPage={currentPage}
                    setCurrentPage={setCurrentPage}
                    pageInfo={data?.page}
                />
            </QueryStateHandler>
        </div>
    );
};

const HousingCompanyFilters = ({filterParams, setFilterParams}) => {
    return (
        <div className="filters">
            <FilterTextInput
                label="Yhtiön nimi"
                filterFieldName="display_name"
                filterParams={filterParams}
                setFilterParams={setFilterParams}
            />
            <FilterTextInput
                label="Osoite"
                filterFieldName="street_address"
                filterParams={filterParams}
                setFilterParams={setFilterParams}
            />
            <FilterPostalCodeInput
                label="Postinumero"
                filterFieldName="postal_code"
                filterParams={filterParams}
                setFilterParams={setFilterParams}
            />
            <RelatedModelFilterCombobox
                label="Rakennuttaja"
                queryFunction={useGetDevelopersQuery}
                labelField="value"
                filterFieldName="developer"
                filterParams={filterParams}
                setFilterParams={setFilterParams}
            />
            <RelatedModelFilterCombobox
                label="Isännöitsijä"
                queryFunction={useGetPropertyManagersQuery}
                labelField="name"
                filterFieldName="property_manager"
                filterParams={filterParams}
                setFilterParams={setFilterParams}
            />
        </div>
    );
};

const HousingCompanyListPage = () => {
    const [filterParams, setFilterParams] = useState({});

    return (
        <div className="companies">
            <h1 className="main-heading">
                <span>Kaikki kohteet</span>
                <Button>Lisää uusi yhtiö</Button>
            </h1>
            <div className="listing">
                <SearchInput
                    className="search"
                    label=""
                    placeholder="Rajaa hakusanalla"
                    searchButtonAriaLabel="Search"
                    clearButtonAriaLabel="Clear search field"
                    onSubmit={(submittedValue) =>
                        // eslint-disable-next-line no-console
                        console.log("Submitted search-value:", submittedValue)
                    }
                />
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
