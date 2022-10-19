import React from "react";

import {IApartmentDetails, IHousingCompanyDetails} from "../models";
import {formatDate, formatMoney} from "../utils";
import {EditButton} from "./index";

interface ImprovementsTableProps {
    data: IApartmentDetails | IHousingCompanyDetails;
    title: string;
    editableType?: "apartment" | "housingCompany";
}

export default function ImprovementsTable({data, title, editableType}: ImprovementsTableProps): JSX.Element {
    // Detect if this is an apartment to know when to show depreciation column
    const showDepreciationPercentage = "links" in data;

    return (
        <div className="list__wrapper list-wrapper--upgrades">
            <h2 className="detail-list__heading">
                {title}
                {editableType !== undefined && (
                    <EditButton
                        state={{[editableType]: data}}
                        pathname={"improvements"}
                        className="pull-right"
                    />
                )}
            </h2>
            <ul className="detail-list__list">
                <li className="detail-list__list-headers">
                    <div>Indeksi</div>
                    <div>Nimi</div>
                    <div>Summa</div>
                    <div>Valmistumispvm</div>
                    {showDepreciationPercentage && <div>Poistoprosentti</div>}
                </li>
                {data.improvements.market_price_index.map((item) => (
                    <li className="detail-list__list-item">
                        <div>Markkinahinta</div>
                        <div>{item.name}</div>
                        <div>{formatMoney(item.value)}</div>
                        <div>{formatDate(item.completion_date)}</div>
                        {showDepreciationPercentage && <div>-</div>}
                    </li>
                ))}
                {data.improvements.construction_price_index.map((item) => (
                    <li className="detail-list__list-item">
                        <div>Rakennuskustannus</div>
                        <div>{item.name}</div>
                        <div>{formatMoney(item.value)}</div>
                        <div>{formatDate(item.completion_date)}</div>
                        {showDepreciationPercentage && <div>{item.depreciation_percentage}%</div>}
                    </li>
                ))}
            </ul>
        </div>
    );
}
