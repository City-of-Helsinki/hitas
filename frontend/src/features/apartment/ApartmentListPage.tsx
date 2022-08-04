import React, {useState} from "react";

import {SearchInput, StatusLabel} from "hds-react";
import {Link} from "react-router-dom";

import {useGetApartmentsQuery} from "../../app/services";
import {FilterCombobox, FilterPostalCodeInput, FilterTextInput} from "../../common/components";
import {IAddress, IApartment, IOwner} from "../../common/models";
import {formatAddress} from "../../common/utils";

interface IApartmentListItem {
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
}: IApartmentListItem) => {
    // Combine owners into a single formatted string
    const ownersString = owners
        .map((o) => `${o.person.last_name}, ${o.person.first_name} (${o.person.social_security_number})`)
        .join(", ");

    return (
        <Link to={`/apartments/${id}`}>
            <li className="results-list__item results-list__item--apartment">
                <div className="number">
                    {stair}
                    {apartmentNumber}
                </div>
                <div className="details">
                    <div className="owner">Omistaja: {ownersString}</div>
                    <div className="rooms">{apartmentType}</div>
                    <div className="area">{surfaceArea} m²</div>
                    <div className="address">{formatAddress(address)}</div>
                    <div className="state">
                        <StatusLabel>{state}</StatusLabel>
                    </div>
                </div>
            </li>
        </Link>
    );
};

export const ApartmentResultsList = ({filterParams}) => {
    const {data, error, isLoading} = useGetApartmentsQuery(filterParams);
    if (error) {
        return (
            <div className="results">
                <ul className="results-list">
                    <p>Error</p>
                </ul>
            </div>
        );
    } else if (isLoading) {
        return (
            <div className="results">
                <ul className="results-list">
                    <p>Loading</p>
                </ul>
            </div>
        );
    } else if (data && data.contents.length) {
        return (
            <div className="results">
                <div>Rekisterin tulokset: {data.page.total_items} yhtiötä</div>
                <div className="list-headers">
                    <div className="list-header apartment">Asunto</div>
                    <div className="list-header area">Pinta-ala</div>
                    <div className="list-header address">Osoite</div>
                    <div className="list-header status">Tila</div>
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
            </div>
        );
    } else {
        return (
            <div className="results">
                <ul className="results-list">
                    <p>Ei tuloksia</p>
                </ul>
            </div>
        );
    }
};

const ApartmentFilters = ({filterParams, setFilterParams}) => {
    return (
        <div className="filters">
            <FilterTextInput
                label="Yhtiön nimi"
                filterFieldName="housing_company_name"
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
            <FilterCombobox
                label="Rakennuttaja"
                options={[{label: "Foo"}, {label: "Bar"}]}
                filterFieldName="developer"
                filterParams={filterParams}
                setFilterParams={setFilterParams}
            />
            <FilterCombobox
                label="Isännöitsijä"
                options={[{label: "Foo"}, {label: "Bar"}]}
                filterFieldName="property_manager"
                filterParams={filterParams}
                setFilterParams={setFilterParams}
            />
        </div>
    );
};

export default function ApartmentListPage() {
    const [filterParams, setFilterParams] = useState({});

    return (
        <div className="apartments">
            <h1 className="main-heading">Kaikki kohteet</h1>
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

                <ApartmentResultsList filterParams={filterParams} />

                <ApartmentFilters
                    filterParams={filterParams}
                    setFilterParams={setFilterParams}
                />
            </div>
        </div>
    );
}
