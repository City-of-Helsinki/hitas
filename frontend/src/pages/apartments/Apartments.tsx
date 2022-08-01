import React from "react";

import {NumberInput, SearchInput, Select, StatusLabel} from "hds-react";
import {Link} from "react-router-dom";

const ApartmentListItem = (apartment) => (
    <Link to={apartment.id}>
        <li className="results-list__item results-list__item--apartment">
            <div className="number">{apartment.number}</div>
            <div className="details">
                <div className="owner">{`Omistaja: ${apartment.owner}, (${apartment.ownerId})`}</div>
                <div className="rooms">{apartment.rooms}</div>
                <div className="area">{apartment.area} m²</div>
                <div className="address">{apartment.address}</div>
                <div className="state">
                    <StatusLabel>{apartment.state}</StatusLabel>
                </div>
            </div>
        </li>
    </Link>
);

export default function Apartments() {
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
                    <div>Rekisterin tulokset: 9037 yhtiötä</div>
                    <div className="list-headers">
                        <div className="list-header apartment">Asunto</div>
                        <div className="list-header area">Pinta-ala</div>
                        <div className="list-header address">Osoite</div>
                        <div className="list-header status">Tila</div>
                    </div>
                    <ul className="results-list">
                        <ApartmentListItem
                            id="abc001"
                            owner="Virtanen, Antti"
                            ownerId="200788-192A"
                            number="A70"
                            rooms="4h,kt,s"
                            area="85.0"
                            address="Peipposentie 3"
                            state="Varattu"
                        />
                        <ApartmentListItem
                            id="abc002"
                            owner="Virtanen, Mirjami"
                            ownerId="190277-181D"
                            number="C2"
                            rooms="1h, kt, s"
                            area="45.0"
                            address="Arabiankatu 5"
                            state="Myyty"
                        />
                        <ApartmentListItem
                            id="abc002"
                            owner="Virtanen, Mirjami"
                            ownerId="190277-181D"
                            number="C2"
                            rooms="1h, kt, s"
                            area="45.0"
                            address="Arabiankatu 5"
                            state="Myyty"
                        />
                        <ApartmentListItem
                            id="abc002"
                            owner="Virtanen, Mirjami"
                            ownerId="190277-181D"
                            number="C2"
                            rooms="1h, kt, s"
                            area="45.0"
                            address="Arabiankatu 5"
                            state="Myyty"
                        />
                        <ApartmentListItem
                            id="abc002"
                            owner="Virtanen, Mirjami"
                            ownerId="190277-181D"
                            number="C2"
                            rooms="1h, kt, s"
                            area="45.0"
                            address="Arabiankatu 5"
                            state="Myyty"
                        />
                        <ApartmentListItem
                            id="abc002"
                            owner="Virtanen, Mirjami"
                            ownerId="190277-181D"
                            number="C2"
                            rooms="1h, kt, s"
                            area="45.0"
                            address="Arabiankatu 5"
                            state="Myyty"
                        />
                    </ul>
                </div>
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
            </div>
        </div>
    );
}
