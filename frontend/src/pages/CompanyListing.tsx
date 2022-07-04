import React from "react";

import { Button, NumberInput, SearchInput, Select } from "hds-react";

const CompanyListing = () => {
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
                        <div className="list-header">Kohde</div>
                        <div className="list-header">Osoite</div>
                        <div className="list-header">
                            Valmiustila, pvm
                        </div>
                        <div className="list-header">Tila</div>
                    </div>
                    <ul className="results-list">
                        <li className="results-list__item">
                            <div className="name">Aapeli Aava</div>
                            <div className="address">
                                Peipposentie 7, 00720
                            </div>
                            <div className="date-added">1.1.2015</div>
                        </li>
                        <li className="results-list__item">
                            <div className="name">Arabian Unelma</div>
                            <div className="address">
                                Arabiankatu 5, 00550
                            </div>
                            <div className="date-added">1.1.2015</div>
                        </li>
                        <li className="results-list__item">
                            <div className="name">Kesäunelma</div>
                            <div className="address">
                                Sompasaarenlaituri 20, 00540
                            </div>
                            <div className="date-added">1.1.2015</div>
                        </li>
                        <li className="results-list__item">
                            <div className="name">Postipuisto</div>
                            <div className="address">
                                Kustinpolku 12, 00620
                            </div>
                            <div className="date-added">1.1.2015</div>
                        </li>
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

export default CompanyListing;
