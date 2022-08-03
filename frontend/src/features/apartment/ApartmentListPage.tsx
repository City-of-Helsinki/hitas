import React from "react";

import {NumberInput, SearchInput, Select, StatusLabel} from "hds-react";
import {Link} from "react-router-dom";

import {useGetApartmentsQuery} from "../../app/services";
import {IAddress, IApartment, IOwner} from "../../common/models";

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
        <Link to={id}>
            <li className="results-list__item results-list__item--apartment">
                <div className="number">
                    {stair}
                    {apartmentNumber}
                </div>
                <div className="details">
                    <div className="owner">Omistaja: {ownersString}</div>
                    <div className="rooms">{apartmentType}</div>
                    <div className="area">{surfaceArea} m²</div>
                    <div className="address">
                        {address.street}, {address.postal_code}
                    </div>
                    <div className="state">
                        <StatusLabel>{state}</StatusLabel>
                    </div>
                </div>
            </li>
        </Link>
    );
};

const ApartmentResultsList = ({items, page}) => {
    if (items.length) {
        return (
            <>
                <div>Rekisterin tulokset: {page.total_items} yhtiötä</div>
                <div className="list-headers">
                    <div className="list-header apartment">Asunto</div>
                    <div className="list-header area">Pinta-ala</div>
                    <div className="list-header address">Osoite</div>
                    <div className="list-header status">Tila</div>
                </div>
                <ul className="results-list">
                    {items.map((item: IApartment) => (
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
    } else {
        return (
            <ul className="results-list">
                <p>Ei tuloksia</p>
            </ul>
        );
    }
};

const ApartmentFilters = () => {
    return (
        <div className="filters">
            <Select
                label="Yhtiön nimi"
                options={[{label: "Foo"}, {label: "Bar"}]}
            />
            <Select
                label="Osoite"
                options={[{label: "Foo"}, {label: "Bar"}]}
            />
            <NumberInput
                label="Postinumero"
                id="postinumeroFiltteri"
            />
            <Select
                label="Rakennuttaja"
                options={[{label: "Foo"}, {label: "Bar"}]}
            />
            <Select
                label="Isännöitsijä"
                options={[{label: "Foo"}, {label: "Bar"}]}
            />
        </div>
    );
};

export default function ApartmentListPage() {
    const {data, error, isLoading} = useGetApartmentsQuery("");

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

                <div className="results">
                    {error ? (
                        <>Oh no, there was an error</>
                    ) : isLoading ? (
                        <>Loading...</>
                    ) : data ? (
                        <ApartmentResultsList
                            items={data.contents}
                            page={data.page}
                        />
                    ) : null}
                </div>

                <ApartmentFilters />
            </div>
        </div>
    );
}
