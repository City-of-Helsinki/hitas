import React from "react";

import {Button, NumberInput, SearchInput, Select} from "hds-react";
import {Link} from "react-router-dom";

import {useGetHousingCompaniesQuery} from "../../app/services";
import {IHousingCompany} from "../../common/models";

const HousingCompanyListItem = ({id, name, address, date}) => {
    return (
        <Link to={id}>
            <li className="results-list__item">
                <div className="name">{name}</div>
                <div className="address">
                    {address.street}, {address.postal_code}
                </div>
                <div className="date">{date}</div>
            </li>
        </Link>
    );
};

const HousingCompanyResultsList = ({items, page}) => {
    if (items.length) {
        return (
            <>
                <div>Rekisterin tulokset: {page.total_items} yhtiötä</div>
                <div className="list-headers">
                    <div className="list-header name">Yhtiö</div>
                    <div className="list-header address">Osoite</div>
                    <div className="list-header date">Valmiustila, pvm</div>
                </div>
                <ul className="results-list">
                    {items.map((item: IHousingCompany) => (
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
    } else {
        return (
            <ul className="results-list">
                <p>Ei tuloksia</p>
            </ul>
        );
    }
};

const HousingCompanyFilters = () => {
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

const HousingCompanyListPage = () => {
    const {data, error, isLoading} = useGetHousingCompaniesQuery("");

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
                <div className="results">
                    {error ? (
                        <>Oh no, there was an error</>
                    ) : isLoading ? (
                        <>Loading...</>
                    ) : data ? (
                        <HousingCompanyResultsList
                            items={data.contents}
                            page={data.page}
                        />
                    ) : null}
                </div>
                <HousingCompanyFilters />
            </div>
        </div>
    );
};

export default HousingCompanyListPage;
