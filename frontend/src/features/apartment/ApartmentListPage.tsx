import React, {useState} from "react";

import {Checkbox, SearchInput, StatusLabel, TextInput} from "hds-react";
import {Link} from "react-router-dom";

import {useGetApartmentsQuery} from "../../app/services";
import {FilterPostalCodeField, FilterTextInputField, ListPageNumbers, QueryStateHandler} from "../../common/components";
import {IAddress, IApartment, IApartmentListResponse, IOwner} from "../../common/models";
import {formatAddress} from "../../common/utils";

interface ApartmentListItemProps {
    id: string;
    apartmentNumber: number;
    stair: string;
    owners: IOwner[];
    apartmentType: string;
    surfaceArea: number;
    address: IAddress;
    state: string;
}

const ApartmentListItem = ({
    id,
    apartmentNumber,
    stair,
    owners,
    apartmentType,
    surfaceArea,
    address,
    state,
}: ApartmentListItemProps): JSX.Element => {
    // Combine owners into a single formatted string
    const ownersString = owners
        .map((o) => `${o.person.last_name} ${o.person.first_name} (${o.person.social_security_number})`)
        .join(", ");

    return (
        <Link to={`/apartments/${id}`}>
            <li className="results-list__item results-list__item--apartment">
                <div className="number">
                    {stair}
                    {apartmentNumber}
                </div>
                <div className="details">
                    <div className="owner">{`Omistaja: ${ownersString}`}</div>
                    <div className="rooms">{apartmentType}</div>
                    <div className="area">{surfaceArea} m²</div>
                    <div className="address">{formatAddress(address)}</div>
                </div>
                <div className="state">
                    <StatusLabel>{state}</StatusLabel>
                </div>
            </li>
        </Link>
    );
};

export const ApartmentResultsList = ({filterParams}): JSX.Element => {
    const [currentPage, setCurrentPage] = useState(1);
    const {data, error, isLoading} = useGetApartmentsQuery({...filterParams, page: currentPage});

    const LoadedApartmentResultsList = ({data}: {data: IApartmentListResponse}) => {
        return (
            <>
                <div className="list-amount">
                    Haun tulokset: {data.page.total_items} {data.page.total_items > 1 ? "yhtiötä" : "yhtiö"}
                </div>
                <div className="list-headers">
                    <div className="list-header apartment">Asunto</div>
                    <div className="list-header area">Pinta-ala</div>
                    <div className="list-header address">Osoite</div>
                    <div className="list-header state">Tila</div>
                </div>
                <ul className="results-list">
                    {data.contents.map((item: IApartment) => (
                        <ApartmentListItem
                            key={item.id}
                            id={item.id}
                            apartmentNumber={item.apartment_number}
                            stair={item.stair}
                            owners={item.owners}
                            apartmentType={item.apartment_type}
                            surfaceArea={item.surface_area}
                            address={item.address}
                            state={item.state}
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
                <LoadedApartmentResultsList data={data as IApartmentListResponse} />
                <ListPageNumbers
                    currentPage={currentPage}
                    setCurrentPage={setCurrentPage}
                    pageInfo={data?.page}
                />
            </QueryStateHandler>
            <></>
        </div>
    );
};

const ApartmentFilters = ({filterParams, setFilterParams}): JSX.Element => {
    return (
        <div className="filters">
            <FilterTextInputField
                label="Osoite"
                filterFieldName="street_address"
                filterParams={filterParams}
                setFilterParams={setFilterParams}
            />
            <FilterPostalCodeField
                label="Postinumero"
                filterFieldName="postal_code"
                filterParams={filterParams}
                setFilterParams={setFilterParams}
            />
            <FilterTextInputField
                label="Yhtiön nimi"
                filterFieldName="housing_company_name"
                filterParams={filterParams}
                setFilterParams={setFilterParams}
            />
            <FilterTextInputField
                label="Omistajan nimi"
                filterFieldName="owner_name"
                filterParams={filterParams}
                setFilterParams={setFilterParams}
            />
            <FilterTextInputField
                label="Henkilötunnus"
                filterFieldName="owner_social_security_number"
                filterParams={filterParams}
                setFilterParams={setFilterParams}
            />
            <TextInput
                id="filter__ostajaehdokas"
                label={"Ostajaehdokas"}
                disabled
            />
            <Checkbox
                id="sales_condition"
                label="Löytyy myyntiehto"
                disabled={true}
            />
        </div>
    );
};

const ApartmentListPage = (): JSX.Element => {
    const [filterParams, setFilterParams] = useState({});

    return (
        <div className="view--apartments-listing">
            <h1 className="main-heading">Kaikki kohteet</h1>
            <div className="listing">
                <SearchInput
                    className="search"
                    label=""
                    placeholder="Rajaa hakusanalla"
                    searchButtonAriaLabel="Search"
                    clearButtonAriaLabel="Clear search field"
                    onSubmit={(
                        submittedValue // eslint-disable-next-line no-console
                    ) => console.log("Submitted search-value:", submittedValue)}
                />

                <ApartmentResultsList filterParams={filterParams} />

                <ApartmentFilters
                    filterParams={filterParams}
                    setFilterParams={setFilterParams}
                />
            </div>
        </div>
    );
};

export default ApartmentListPage;
