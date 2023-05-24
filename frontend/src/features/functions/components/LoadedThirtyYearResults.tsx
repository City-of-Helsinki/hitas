import {Dialog} from "hds-react";
import {useState} from "react";
import {CloseButton, Heading} from "../../../common/components";
import {ComparisonResultListItem, ComparisonSkippedList} from "./";

const LoadedThirtyYearComparison = ({data, calculationDate, reCalculateFn}): JSX.Element => {
    const automaticallyReleased = data?.automatically_released ?? [];
    const releasedFromRegulation = data?.released_from_regulation ?? [];
    const releasedCompanies = [...automaticallyReleased, ...releasedFromRegulation];
    const stayingCompanies = data?.stays_regulated ?? [];
    const skippedCompanies = data?.skipped ?? [];
    const obfuscatedOwners = data?.obfuscated_owners ?? [];
    const [isModalOpen, setIsModalOpen] = useState(obfuscatedOwners.length > 0);

    const ListItems = ({list}) => {
        return list.map((item, idx) => (
            <ComparisonResultListItem
                company={item}
                key={idx}
            />
        ));
    };

    const ResultsList = ({category}) => (
        <div className={`companies companies--${category}`}>
            <Heading type="body">
                {category === "freed" ? "Valvonnasta vapautuvat " : "Valvonnan piiriin jäävät "}
                yhtiöt
            </Heading>
            <div className="list">
                {releasedCompanies.length > 0 ? (
                    <>
                        <div className="list-headers">
                            <div className="list-header name">Nimi</div>
                            <div className="list-header address">Osoite</div>
                            <div className="list-header date">Valmistunut</div>
                            <div className="list-header property-manager">Isännöitsijä</div>
                        </div>
                        <ul className="results-list">
                            {category === "freed" ? (
                                <ListItems list={releasedCompanies} />
                            ) : (
                                <ListItems list={stayingCompanies} />
                            )}
                        </ul>
                    </>
                ) : (
                    <p>Ei listattavia yhtiöitä</p>
                )}
            </div>
        </div>
    );

    if (skippedCompanies.length > 0)
        return (
            <ComparisonSkippedList
                companies={skippedCompanies}
                calculationDate={calculationDate}
                reCalculateFn={reCalculateFn}
            />
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
};

export default LoadedThirtyYearComparison;
