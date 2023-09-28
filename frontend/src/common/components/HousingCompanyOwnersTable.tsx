import React from "react";
import {LoadingSpinner} from "hds-react";
import {useGetHousingCompanyOwnersQuery} from "../services";

export default function HousingCompanyOwnersTable({housingCompanyId}: {housingCompanyId: string}): React.JSX.Element {
    const {
        data: housingCompanyOwners,
        isLoading: isHousingCompanyOwnersLoading,
        error: housingCompanyOwnersError,
    } = useGetHousingCompanyOwnersQuery(housingCompanyId);

    return (
        <ul className="detail-list__list detail-list__list--owners">
            {housingCompanyOwners?.length ? (
                <>
                    <li className="detail-list__list-headers">
                        <div>
                            Asunnon
                            <br />
                            numero
                        </div>
                        <div>
                            Asunnon <br />
                            pinta-ala
                        </div>
                        <div>Osakenumerot</div>
                        <div>Kauppakirjapäivä</div>
                        <div>Nimi</div>
                        <div>Henkilötunnus</div>
                    </li>
                    {housingCompanyOwners.map((item, index) => (
                        <li
                            className="detail-list__list-item"
                            key={`owner-item-${index}`}
                        >
                            <div>{item.number}</div>
                            <div>{item.surface_area}</div>
                            <div>{item.share_numbers}</div>
                            <div>{item.purchase_date}</div>
                            <div>{item.owner_name}</div>
                            <div>{item.owner_ssn}</div>
                        </li>
                    ))}
                </>
            ) : (
                <>
                    {!housingCompanyOwners?.length && !housingCompanyOwnersError && !isHousingCompanyOwnersLoading && (
                        <p>Ei omistajia</p>
                    )}
                    {isHousingCompanyOwnersLoading && (
                        <div className="spinner-wrap">
                            <LoadingSpinner />
                        </div>
                    )}
                    {housingCompanyOwnersError && (
                        <div>
                            <p>Virhe rajapintakutsussa 😞</p>
                        </div>
                    )}
                </>
            )}
        </ul>
    );
}
