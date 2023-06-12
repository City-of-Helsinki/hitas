import {Dialog} from "hds-react";
import {useState} from "react";
import {CloseButton, Heading} from "../../../common/components";
import {ThirtyYearResultListItem, ThirtyYearSkippedList} from "./";

const ThirtyYearLoadedResults = ({data, calculationDate, reCalculateFn}): JSX.Element => {
    const automaticallyReleased = data?.automatically_released ?? [];
    const releasedFromRegulation = data?.released_from_regulation ?? [];
    const releasedCompanies = [...automaticallyReleased, ...releasedFromRegulation];
    const stayingCompanies = data?.stays_regulated ?? [];
    const skippedCompanies = data?.skipped ?? [];
    const obfuscatedOwners = data?.obfuscated_owners ?? [];
    const [isModalOpen, setIsModalOpen] = useState(obfuscatedOwners.length > 0);
    const [isNoCompaniesModalOpen, setIsNoCompaniesModalOpen] = useState(true);

    const ResultsList = ({category}) => {
        const companies = category === "freed" ? releasedCompanies : stayingCompanies;
        return (
            <div className={`companies companies--${category}`}>
                <Heading type="body">
                    {category === "freed" ? "Valvonnasta vapautuvat " : "Valvonnan piiriin jäävät "}
                    yhtiöt
                </Heading>
                <div className="list">
                    {companies.length > 0 ? (
                        <div className="list-headers">
                            <div className="list-header name">Nimi ja osoite</div>
                            <div className="list-header date">Valmistumispäivä</div>
                            <div className="list-header property-manager">
                                Isännöitsijätiedot
                                <br />
                                päivitetty viimeksi
                            </div>
                        </div>
                    ) : (
                        <p>Ei listattavia yhtiöitä.</p>
                    )}
                    <ul className="results-list">
                        {companies.map((item, idx) => (
                            <ThirtyYearResultListItem
                                company={item}
                                calculationDate={calculationDate}
                                category={category}
                                key={idx}
                            />
                        ))}
                    </ul>
                </div>
            </div>
        );
    };

    if (skippedCompanies.length > 0)
        return (
            <ThirtyYearSkippedList
                companies={skippedCompanies}
                calculationDate={calculationDate}
                reCalculateFn={reCalculateFn}
            />
        );
    else if (releasedCompanies.length === 0 && stayingCompanies.length === 0)
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
    else
        return (
            <>
                <>
                    <ResultsList category="freed" />
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
                            {obfuscatedOwners.sort().map((owner, idx) => (
                                <li key={idx}>{owner.name}</li>
                            ))}
                        </ul>
                    </Dialog.Content>
                    <Dialog.ActionButtons>
                        <CloseButton onClick={() => setIsModalOpen(false)} />
                    </Dialog.ActionButtons>
                </Dialog>
            </>
        );
};

export default ThirtyYearLoadedResults;
