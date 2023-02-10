import React from "react";

import {IconLock, IconLockOpen} from "hds-react";
import {Link, useLocation} from "react-router-dom";

import {Heading, NavigateBackButton} from "../../common/components";
import {IApartmentDetails, IConditionOfSale} from "../../common/models";
import {formatAddress, formatDate} from "../../common/utils";

const ApartmentSalesConditionsPage = () => {
    const {state}: {state: {apartment: IApartmentDetails}} = useLocation();
    const conditionsOfSale = state.apartment.conditions_of_sale;

    return (
        <div className="view--create view--apartment-conditions-of-sale">
            <Heading type="main">Myyntiehdot</Heading>
            <ul className="conditions-of-sale-list">
                {conditionsOfSale.length ? (
                    <>
                        <li className="conditions-of-sale-headers">
                            <header>Omistaja</header>
                            <header>Asunto</header>
                            <header>Lisäaika</header>
                            <header>Toteutunut</header>
                        </li>
                        {conditionsOfSale.map((cos: IConditionOfSale) => (
                            <li
                                key={`conditions-of-sale-item-${cos.id}`}
                                className={`conditions-of-sale-list-item${cos.fulfilled ? " resolved" : " unresolved"}`}
                            >
                                <div className="input-wrap">
                                    {cos.fulfilled ? <IconLockOpen /> : <IconLock />}
                                    {cos.owner.name} ({cos.owner.identifier})
                                </div>
                                <div className="input-wrap">
                                    <Link
                                        to={`/housing-companies/${cos.apartment.housing_company.id}/apartments/${cos.apartment.id}`}
                                    >
                                        {formatAddress(cos.apartment.address)}
                                    </Link>
                                </div>
                                <div className="input-wrap">{cos.grace_period}</div>
                                <div className="input-wrap">{formatDate(cos.fulfilled)} </div>
                            </li>
                        ))}
                    </>
                ) : (
                    <div>Ei myyntiehtoja</div>
                )}
            </ul>
            <div className="row row--buttons">
                <NavigateBackButton />
            </div>
        </div>
    );
};

export default ApartmentSalesConditionsPage;
