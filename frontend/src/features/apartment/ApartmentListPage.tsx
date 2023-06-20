import {useState} from "react";

import {IconSearch, LoadingSpinner, StatusLabel} from "hds-react";
import {Link} from "react-router-dom";
import {useGetApartmentsQuery, useGetHousingCompanyApartmentsQuery} from "../../app/services";
import {
    FilterIntegerField,
    FilterSelectField,
    FilterTextInputField,
    Heading,
    ListPageNumbers,
    QueryStateHandler,
} from "../../common/components";
import FilterCheckboxField from "../../common/components/FilterCheckboxField";
import {getApartmentSoldStatusLabel} from "../../common/localisation";
import {IApartment, IApartmentListResponse} from "../../common/schemas";
import {formatDate} from "../../common/utils";
import ConditionsOfSaleStatus from "./components/ConditionsOfSaleStatus";

const ApartmentListItem = ({apartment}: {apartment: IApartment}): JSX.Element => {
    // Combine ownerships into a single formatted string
    const ownershipsString = apartment.ownerships.length
        ? apartment.ownerships.map((o) => `${o.owner.name} (${o.owner.identifier})`).join(", ")
        : "Ei omistajuuksia";

    const isHousingCompanyReleased = apartment.links.housing_company.regulation_status.startsWith("released");
    return (
        <Link to={`/housing-companies/${apartment.links.housing_company.id}/apartments/${apartment.id}`}>
            <li className="results-list__item results-list__item--apartment">
                <div className="apartment-number">
                    <span className="stair-and-number">
                        {apartment.address.stair}
                        {apartment.address.apartment_number}
                    </span>
                    <ConditionsOfSaleStatus apartment={apartment} />
                </div>
                <div className="address-and-housing-company">
                    <div className="housing-company">{apartment.links.housing_company.display_name}</div>
                    <div className="address">
                        <div className="street-address">
                            {apartment.address.street_address} {apartment.address.stair}{" "}
                            {apartment.address.apartment_number}
                        </div>
                        <div className="postal-code">
                            {apartment.address.postal_code}, {apartment.address.city}
                        </div>
                    </div>
                </div>
                <div className="owners-and-area">
                    <div className="ownership">{`${ownershipsString}`}</div>
                    <div className="surface-area">
                        {`${apartment.surface_area ? apartment.surface_area + "m²" : ""}
                        ${apartment.rooms ?? ""} ${apartment.type ?? ""}`}
                    </div>
                </div>
                <div className="state">
                    <StatusLabel>
                        {isHousingCompanyReleased ? "Vapautunut" : getApartmentSoldStatusLabel(apartment)}
                    </StatusLabel>
                    {!isHousingCompanyReleased && (
                        <StatusLabel>
                            {apartment.completion_date ? formatDate(apartment.completion_date) : "Ei valmis"}
                        </StatusLabel>
                    )}
                </div>
            </li>
        </Link>
    );
};

const LoadedApartmentResultsList = ({data, isFetching}: {data: IApartmentListResponse; isFetching: boolean}) => {
    return (
        <>
            <div className="list-headers">
                <div className="list-header apartment-number">Asunto</div>
                <div className="list-header address-and-housing-company">Osoite</div>
                <div className="list-header owners-and-area">Omistajuudet / Asunnon tiedot</div>
                <div className="list-header state">Tila / Valmistumispvm</div>
            </div>
            <ul className={`results-list${isFetching ? " results-list-blurred" : ""}`}>
                {isFetching && (
                    <div className="results-list-overlay-spinner">
                        <LoadingSpinner />
                    </div>
                )}
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

function result(data, error, isLoading, isFetching, currentPage, setCurrentPage) {
    return (
        <div className="results results--apartment">
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <LoadedApartmentResultsList
                    data={data as IApartmentListResponse}
                    isFetching={isFetching}
                />
                <ListPageNumbers
                    currentPage={currentPage}
                    setCurrentPage={setCurrentPage}
                    pageInfo={data?.page}
                />
            </QueryStateHandler>
            {!isLoading ? (
                <div className="list-amount">
                    Haun tulokset: {data?.page.total_items} {data?.page.total_items === 1 ? "asunto" : "asuntoa"}
                </div>
            ) : null}
        </div>
    );
}

export const ApartmentResultsList = ({filterParams}): JSX.Element => {
    const [currentPage, setCurrentPage] = useState(1);
    const {data, error, isLoading, isFetching} = useGetApartmentsQuery({...filterParams, page: currentPage});

    return result(data, error, isLoading, isFetching, currentPage, setCurrentPage);
};

export const HousingCompanyApartmentResultsList = ({housingCompanyId}): JSX.Element => {
    const [currentPage, setCurrentPage] = useState(1);
    const {data, error, isLoading, isFetching} = useGetHousingCompanyApartmentsQuery({
        housingCompanyId: housingCompanyId,
        params: {page: currentPage},
    });

    return result(data, error, isLoading, isFetching, currentPage, setCurrentPage);
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
            <FilterIntegerField
                label="Postinumero"
                minLength={5}
                maxLength={5}
                filterFieldName="postal_code"
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
                <div className="search">
                    <FilterTextInputField
                        label=""
                        filterFieldName="housing_company_name"
                        filterParams={filterParams}
                        setFilterParams={setFilterParams}
                    />
                    <IconSearch />
                </div>

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
