import {useState} from "react";

import {SearchInput, StatusLabel} from "hds-react";
import {Link} from "react-router-dom";
import {useGetApartmentsQuery, useGetHousingCompanyApartmentsQuery} from "../../app/services";
import {
    FilterIntegerField,
    FilterTextInputField,
    Heading,
    ListPageNumbers,
    QueryStateHandler,
} from "../../common/components";
import FilterCheckboxField from "../../common/components/FilterCheckboxField";
import {getApartmentStateLabel} from "../../common/localisation";
import {IApartment, IApartmentListResponse} from "../../common/schemas";
import ConditionsOfSaleStatus from "./components/ConditionsOfSaleStatus";

const ApartmentListItem = ({apartment}: {apartment: IApartment}): JSX.Element => {
    // Combine ownerships into a single formatted string
    const ownershipsString = apartment.ownerships.length
        ? apartment.ownerships.map((o) => `${o.owner.name} (${o.owner.identifier})`).join(", ")
        : "Ei omistajuuksia";
    return (
        <Link to={`/housing-companies/${apartment.links.housing_company.id}/apartments/${apartment.id}`}>
            <li className="results-list__item results-list__item--apartment">
                <div className="number">
                    {apartment.address.stair}
                    {apartment.address.apartment_number}
                </div>
                <div className="details">
                    <div className="housing-company">{apartment.links.housing_company.display_name}</div>
                    <div className="ownership">{`${ownershipsString}`}</div>
                    <div className="address">
                        <div className="street-address">
                            {apartment.address.street_address} {apartment.address.stair}{" "}
                            {apartment.address.apartment_number}
                        </div>
                        <div className="postal-code">
                            {apartment.address.postal_code}, {apartment.address.city}
                        </div>
                    </div>
                    <div className="area">
                        {`${apartment.surface_area ? apartment.surface_area + "m²" : ""}
                        ${apartment.rooms || ""} ${apartment.type}`}
                    </div>
                </div>
                <div className="state">
                    <ConditionsOfSaleStatus apartment={apartment} />
                    <StatusLabel>{getApartmentStateLabel(apartment.state)}</StatusLabel>
                </div>
            </li>
        </Link>
    );
};

function result(data, error, isLoading, currentPage, setCurrentPage) {
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
        </div>
    );
}

const LoadedApartmentResultsList = ({data}: {data: IApartmentListResponse}) => {
    return (
        <>
            <div className="list-amount">
                Haun tulokset: {data.page.total_items} {data.page.total_items > 1 ? "asuntoa" : "asunto"}
            </div>
            <div className="list-headers">
                <div className="list-header apartment">Asunto</div>
                <div className="list-header address">Osoite</div>
                <div className="list-header area">Omistajuudet / Asunnon tiedot</div>
                <div className="list-header state">Tila</div>
            </div>
            <ul className="results-list">
                {data.contents.map((item: IApartment) => (
                    <ApartmentListItem
                        key={item.id}
                        apartment={item}
                    />
                ))}
            </ul>
        </>
    );
};

export const ApartmentResultsList = ({filterParams}): JSX.Element => {
    const [currentPage, setCurrentPage] = useState(1);
    const {data, error, isLoading} = useGetApartmentsQuery({...filterParams, page: currentPage});

    return result(data, error, isLoading, currentPage, setCurrentPage);
};

export const HousingCompanyApartmentResultsList = ({housingCompanyId}): JSX.Element => {
    const [currentPage, setCurrentPage] = useState(1);
    const {data, error, isLoading} = useGetHousingCompanyApartmentsQuery({
        housingCompanyId: housingCompanyId,
        params: {page: currentPage},
    });
    return result(data, error, isLoading, currentPage, setCurrentPage);
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
            <FilterTextInputField
                label="Omistajan nimi"
                filterFieldName="owner_name"
                filterParams={filterParams}
                setFilterParams={setFilterParams}
            />
            <FilterTextInputField
                label="Omistajan henkilötunnus tai y-tunnus"
                filterFieldName="owner_identifier"
                filterParams={filterParams}
                setFilterParams={setFilterParams}
            />
            <FilterTextInputField
                label="Yhtiön nimi"
                filterFieldName="housing_company_name"
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
            <FilterCheckboxField
                label="Löytyy myyntiehto"
                filterFieldName="has_conditions_of_sale"
                filterParams={filterParams}
                setFilterParams={setFilterParams}
                applyOnlyOnTrue
            />
        </div>
    );
};

const ApartmentListPage = (): JSX.Element => {
    const [filterParams, setFilterParams] = useState({});

    return (
        <div className="view--apartments-listing">
            <Heading>Kaikki kohteet</Heading>
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
