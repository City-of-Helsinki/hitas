import {Button, ButtonPresetTheme, ButtonSize, ButtonVariant, Dialog} from "hds-react";
import React, {useState} from "react";
import {CloseButton, Divider, Heading} from "../../../common/components";
import {ThirtyYearResultListItem, ThirtyYearSkippedList} from "./index";

const ListHeaders = () => (
    <div className="list-headers">
        <div className="list-header name">Nimi ja osoite</div>
        <div className="list-header date">Valmistumispäivä</div>
        <div className="list-header property-manager">
            Isännöitsijän
            <br />
            sähköpostiosoite
        </div>
    </div>
);

const ThirtyYearLoadedResults = ({data, calculationDate, reCalculateFn}): React.JSX.Element => {
    const automaticallyReleased = data?.automatically_released ?? [];
    const releasedFromRegulation = data?.released_from_regulation ?? [];
    const releasedCompanies = [...automaticallyReleased, ...releasedFromRegulation];
    const stayingCompanies = data?.stays_regulated ?? [];
    const manuallyReleasedCompanies = stayingCompanies.filter(
        (housingCompany) => housingCompany.current_regulation_status !== "regulated"
    );
    const displayedStayingCompanies = stayingCompanies.filter(
        (housingCompany) => housingCompany.current_regulation_status === "regulated"
    );
    const skippedCompanies = data?.skipped ?? [];
    const obfuscatedOwners = data?.obfuscated_owners ?? [];
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isNoCompaniesModalOpen, setIsNoCompaniesModalOpen] = useState(true);

    const ResultsList = ({category}) => {
        const companies = category === "freed" ? releasedCompanies : displayedStayingCompanies;
        const hasManuallyReleasedCompanies = category === "freed" && manuallyReleasedCompanies.length > 0;
        return (
            <div className={`companies companies--${category}`}>
                <Heading type="body">
                    {category === "freed" ? "Valvonnasta vapautetut " : "Valvonnan piiriin jäävät"} yhtiöt
                    {category === "freed" && obfuscatedOwners.length > 0 && (
                        <Button
                            theme={ButtonPresetTheme.Black}
                            variant={ButtonVariant.Secondary}
                            size={ButtonSize.Small}
                            onClick={() => setIsModalOpen((prev) => !prev)}
                            className="obfuscated-owners-button"
                        >
                            Obfuskoidut omistajat
                        </Button>
                    )}
                </Heading>
                <div className="list">
                    <ListHeaders />
                    {companies.length > 0 ? (
                        <>
                            <ul className="results-list">
                                {companies.map((item) => (
                                    <ThirtyYearResultListItem
                                        housingCompany={item}
                                        calculationDate={calculationDate}
                                        category={category}
                                        key={item.id}
                                    />
                                ))}
                            </ul>
                        </>
                    ) : (
                        <p>Vertailussa ei vapautunut yhtiöitä.</p>
                    )}
                    {hasManuallyReleasedCompanies && (
                        <>
                            <h3>Tontit-yksikön päätöksellä vapautetut yhtiöt</h3>
                            <ul className="results-list">
                                {manuallyReleasedCompanies.map((item) => (
                                    <ThirtyYearResultListItem
                                        housingCompany={item}
                                        calculationDate={calculationDate}
                                        category={category}
                                        key={item.id}
                                    />
                                ))}
                            </ul>
                        </>
                    )}
                </div>
            </div>
        );
    };

    if (skippedCompanies.length > 0) {
        return (
            <ThirtyYearSkippedList
                skippedHousingCompanies={skippedCompanies}
                calculationDate={calculationDate}
                reCalculateFn={reCalculateFn}
            />
        );
    } else if (releasedCompanies.length === 0 && stayingCompanies.length === 0) {
        return (
            <Dialog
                className="error-modal"
                id="no-companies-modal"
                aria-labelledby="no-companies-modal"
                isOpen={isNoCompaniesModalOpen}
                close={() => setIsNoCompaniesModalOpen(false)}
                closeButtonLabelText="Sulje"
            >
                <Dialog.Header
                    title="Ei vapautuvia tai valvottavia yhtiöitä"
                    id="no-companies-modal-header"
                />
                <Dialog.Content>
                    Järjestelmä ei palauttanut vertailutulosta, koska kannassa ei ole yhtiöitä mitä verrata.
                </Dialog.Content>
                <Dialog.ActionButtons>
                    <CloseButton onClick={() => setIsNoCompaniesModalOpen(false)} />
                </Dialog.ActionButtons>
            </Dialog>
        );
    } else {
        return (
            <>
                <>
                    <ResultsList category="freed" />
                    <Divider size="s" />
                    <ResultsList category="remaining" />
                </>
                <Dialog
                    id="obfuscated-owners-modal"
                    aria-labelledby="obfuscated-owners-modal"
                    isOpen={isModalOpen}
                >
                    <Dialog.Header
                        id="obfuscated-owners-header"
                        title="Obfuskoidut omistajat"
                    />
                    <Dialog.Content>
                        Vertailun yhteydessä obfuskoidut omistajat:
                        <ul>
                            {obfuscatedOwners.map((owner) => (
                                <li key={owner.id}>{owner.name}</li>
                            ))}
                        </ul>
                    </Dialog.Content>
                    <Dialog.ActionButtons>
                        <CloseButton onClick={() => setIsModalOpen(false)} />
                    </Dialog.ActionButtons>
                </Dialog>
            </>
        );
    }
};

export default ThirtyYearLoadedResults;
