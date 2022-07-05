import { Button, NumberInput, SearchInput, Select } from "hds-react";
import React from "react";

type ListItemProps = {
    name: string;
    address: string;
    dateAdded: Date | string;
};

const CompanyListItem = (props: ListItemProps) => {
    return (
        <li className="results-list__item">
            <div className="name">{props.name}</div>
            <div className="address">{props.address}</div>
            <div className="date-added">
                {props.dateAdded as string}
            </div>
        </li>
    );
};

const Companies = () => {
    return (
        <div className="company-listing">
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
                        console.log(
                            "Submitted search-value:",
                            submittedValue
                        )
                    }
                />
                <div className="results">
                    <div>Rekisterin tulokset: 9037 yhtiötä</div>
                    <div className="list-headers">
                        <div className="list-header name">Yhtiö</div>
                        <div className="list-header address">
                            Osoite
                        </div>
                        <div className="list-header date-added">
                            Valmiustila, pvm
                        </div>
                    </div>
                    <ul className="results-list">
                        <CompanyListItem
                            name="Aapeli Aava"
                            address="Peipposentie 7, 00720"
                            dateAdded="1.1.2015"
                        />
                        <CompanyListItem
                            name="Arabian Unelma"
                            address="Arabiankatu 5, 00540"
                            dateAdded="1.1.2015"
                        />
                        <CompanyListItem
                            name="Kesäunelma"
                            address="Sompasaarenlaituri 20, 00540"
                            dateAdded="1.1.2015"
                        />
                        <CompanyListItem
                            name="Postipuisto"
                            address="Kustinpolku 12, 00620"
                            dateAdded="1.1.2015"
                        />
                        <CompanyListItem
                            name="Aapeli Aava"
                            address="Peipposentie 7, 00720"
                            dateAdded="1.1.2015"
                        />
                        <CompanyListItem
                            name="Arabian Unelma"
                            address="Arabiankatu 5, 00540"
                            dateAdded="1.1.2015"
                        />
                        <CompanyListItem
                            name="Kesäunelma"
                            address="Sompasaarenlaituri 20, 00540"
                            dateAdded="1.1.2015"
                        />
                        <CompanyListItem
                            name="Postipuisto"
                            address="Kustinpolku 12, 00620"
                            dateAdded="1.1.2015"
                        />
                        <CompanyListItem
                            name="Postipuisto"
                            address="Kustinpolku 12, 00620"
                            dateAdded="1.1.2015"
                        />
                    </ul>
                </div>
                <div className="filters">
                    <Select
                        label="Yhtiön nimi"
                        options={[{ label: "Foo" }, { label: "Bar" }]}
                    />
                    <Select
                        label="Osoite"
                        options={[{ label: "Foo" }, { label: "Bar" }]}
                    />
                    <NumberInput
                        label="Postinumero"
                        id="postinumeroFiltteri"
                    />
                    <Select
                        label="Rakennuttaja"
                        options={[{ label: "Foo" }, { label: "Bar" }]}
                    />
                    <Select
                        label="Isännöitsijä"
                        options={[{ label: "Foo" }, { label: "Bar" }]}
                    />
                </div>
            </div>
        </div>
    );
};

export default Companies;
