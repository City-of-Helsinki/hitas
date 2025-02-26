import {Button, ButtonPresetTheme, ButtonSize, IconHistory, StatusLabel} from "hds-react";
import {Link, useLocation, useParams} from "react-router-dom";

import {EditButton, GenericActionModal, Heading, QueryStateHandler} from "../../../common/components";
import {getHousingCompanyHitasTypeName, getHousingCompanyRegulationStatusName} from "../../../common/localisation";
import {IHousingCompanyDetails} from "../../../common/schemas";
import {useGetHousingCompanyDetailQuery, usePatchHousingCompanyMutation} from "../../../common/services";
import React, {useState} from "react";
import {formatDate, hdsToast} from "../../../common/utils";

const CancelHousingCompanyRegulationReleaseButton = ({
    housingCompany,
    isHousingCompanySubPage,
}: {
    housingCompany: IHousingCompanyDetails;
    isHousingCompanySubPage: boolean;
}) => {
    const [isModalOpen, setIsModalOpen] = useState(false);

    const [patchHousingCompany] = usePatchHousingCompanyMutation();

    // Cancel release button is visible only if the housing company is released by plot department,
    // and the release date is less than three months ago
    const threeMonthsAgo = new Date();
    threeMonthsAgo.setMonth(threeMonthsAgo.getMonth() - 3);

    const isCancelReleaseButtonVisible =
        housingCompany.regulation_status === "released_by_plot_department" &&
        !isHousingCompanySubPage &&
        housingCompany.release_date !== null &&
        new Date(housingCompany.release_date) > threeMonthsAgo;

    if (!isCancelReleaseButtonVisible) return <></>;

    const handleCancelHousingCompanyRelease = () => {
        patchHousingCompany({
            housingCompanyId: housingCompany.id,
            data: {regulation_status: "regulated"},
        })
            .then(() => {
                hdsToast.success(`${housingCompany.name.display} on nyt asetettu takaisin sääntelyn piiriin.`);
            })
            .catch(() => {
                hdsToast.error(`${housingCompany.name.display} asettaminen takaisin sääntelyn piiriin epäonnistui.`);
            });
        setIsModalOpen(false);
    };

    return (
        <>
            <Button
                theme={ButtonPresetTheme.Black}
                size={ButtonSize.Small}
                iconStart={<IconHistory />}
                onClick={() => setIsModalOpen(true)}
            >
                Peruuta vapautus
            </Button>

            <GenericActionModal
                title="Peruuta yhtiön sääntelystä vapautus"
                modalIcon={<IconHistory />}
                isModalOpen={isModalOpen}
                closeModal={() => setIsModalOpen(false)}
                confirmButton={
                    <Button
                        theme={ButtonPresetTheme.Black}
                        size={ButtonSize.Small}
                        iconStart={<IconHistory />}
                        onClick={handleCancelHousingCompanyRelease}
                    >
                        Peruuta vapautus
                    </Button>
                }
            >
                <p>Haluatko peruuttaa yhtiön vapautumisen, ja asettaa sen takaisin sääntelyn piiriin?</p>
                <p>
                    Yhtiö: <b>{housingCompany.name.display}</b>
                </p>
                <p>
                    Yhtiön vapautuspäivämäärä: <b>{formatDate(housingCompany.release_date)}</b>
                </p>
            </GenericActionModal>
        </>
    );
};

const HousingCompanyHeaderContent = ({housingCompany}: {housingCompany: IHousingCompanyDetails}) => {
    const {pathname} = useLocation();
    const isHousingCompanySubPage = pathname.split("/").pop() !== housingCompany.id;

    // Edit button is visible only if the user is on the housing company main page
    const isEditButtonVisible = !isHousingCompanySubPage;

    return (
        <>
            <div>
                {isHousingCompanySubPage ? (
                    <Link to={`/housing-companies/${housingCompany.id}`}>
                        <Heading type="main">{housingCompany.name.display}</Heading>
                    </Link>
                ) : (
                    <Heading type="main">
                        {housingCompany.name.display}
                        {isEditButtonVisible ? <EditButton /> : null}
                        <CancelHousingCompanyRegulationReleaseButton
                            housingCompany={housingCompany}
                            isHousingCompanySubPage={isHousingCompanySubPage}
                        />
                    </Heading>
                )}
            </div>
            <div>
                <StatusLabel>{getHousingCompanyHitasTypeName(housingCompany.hitas_type)}</StatusLabel>
                <StatusLabel>{housingCompany.completed ? "Valmis" : "Ei valmis"}</StatusLabel>

                {housingCompany.completed ? (
                    <>
                        {housingCompany.hitas_type !== "half_hitas" ? (
                            <StatusLabel>
                                {housingCompany.over_thirty_years_old ? "Yli 30 vuotta" : "Alle 30 vuotta"}
                            </StatusLabel>
                        ) : null}
                        <StatusLabel>
                            {getHousingCompanyRegulationStatusName(housingCompany.regulation_status)}
                        </StatusLabel>
                    </>
                ) : null}

                {housingCompany.hitas_type === "rr_new_hitas" && <StatusLabel>Ryhmärakentamiskohde</StatusLabel>}

                {housingCompany.exclude_from_statistics ? <StatusLabel>Ei tilastoihin</StatusLabel> : null}
            </div>
        </>
    );
};

const HousingCompanyHeader = () => {
    const {housingCompanyId}: {housingCompanyId?: string} = useParams();

    const {data, error, isLoading} = useGetHousingCompanyDetailQuery(housingCompanyId as string, {
        skip: !housingCompanyId,
    });

    if (!housingCompanyId) {
        return <Heading>Uusi taloyhtiö</Heading>;
    }

    return (
        <div className="housing-company-header">
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <HousingCompanyHeaderContent housingCompany={data as IHousingCompanyDetails} />
            </QueryStateHandler>
        </div>
    );
};

export default HousingCompanyHeader;
