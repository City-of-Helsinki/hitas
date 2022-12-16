import React from "react";

import {IApartmentDetails, IHousingCompanyDetails} from "../models";
import {formatMoney} from "../utils";
import {EditButton, Heading} from "./index";

interface ImprovementsTableProps {
    data: IApartmentDetails | IHousingCompanyDetails;
    title: string;
    editableType?: "apartment" | "housingCompany";
    editPath?: string;
}

export default function ImprovementsTable({data, title, editableType, editPath}: ImprovementsTableProps): JSX.Element {
    // Detect if this is an apartment to know when to show depreciation column
    const isApartment = "links" in data;

    return (
        <div className="list__wrapper list-wrapper--upgrades">
            <Heading type="list">
                <span>{title}</span>
                {editableType !== undefined && (
                    <EditButton
                        state={{[editableType]: data}}
                        pathname={editPath || "improvements"}
                        className="pull-right"
                    />
                )}
            </Heading>
            <ul className="detail-list__list">
                {data.improvements.market_price_index.length || data.improvements.construction_price_index.length ? (
                    <>
                        <li className="detail-list__list-headers">
                            <div>Indeksi</div>
                            <div>Nimi</div>
                            <div>Summa</div>
                            <div>Valmistumiskuukausi</div>
                            {isApartment && <div>Poistoprosentti</div>}
                        </li>
                        {data.improvements.market_price_index.map((item, index) => (
                            <li
                                className="detail-list__list-item"
                                key={`market-item-${index}`}
                            >
                                <div>Markkinahinta</div>
                                <div>{item.name}</div>
                                <div>{formatMoney(item.value)}</div>
                                <div>{item.completion_date}</div>
                                {isApartment && <div>-</div>}
                            </li>
                        ))}
                        {data.improvements.construction_price_index.map((item, index) => (
                            <li
                                className="detail-list__list-item"
                                key={`market-item-${index}`}
                            >
                                <div>Rakennuskustannus</div>
                                <div>{item.name}</div>
                                <div>{formatMoney(item.value)}</div>
                                <div>{item.completion_date}</div>
                                {isApartment && <div>{item.depreciation_percentage}%</div>}
                            </li>
                        ))}
                    </>
                ) : (
                    <p>Ei parannuksia</p>
                )}
            </ul>
        </div>
    );
}
