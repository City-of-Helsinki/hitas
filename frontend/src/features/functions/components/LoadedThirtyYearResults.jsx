import {Heading} from "../../../common/components";
import {ComparisonResultListItem} from "./";

const LoadedThirtyYearComparison = ({data}) => {
    if (data?.error !== undefined) return <h3>Error: {data.error}</h3>; // For testing purposes - error's shouldn't get here
    const automaticallyReleased = data?.automatically_released ?? [];
    const releasedFromRegulation = data?.released_from_regulation ?? [];
    const releasedCompanies = [...automaticallyReleased, ...releasedFromRegulation];
    const stayingCompanies = data?.stays_regulated ?? [];

    const ListItems = ({list}) => {
        if (list.length < 1) return <p>Ei yhtiöitä!</p>;
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
                {category === "freed" ? "Vapautuneet " : "Valvonnan piiriin jäävät "}
                yhtiöt
            </Heading>
            <div className="list">
                <div className="list-headers">
                    <div className="list-header name">Nimi</div>
                    <div className="list-header address">Osoite</div>
                    <div className="list-header date">Valmistunut</div>
                </div>
                {releasedCompanies.length > 0 ? (
                    <ul className="results-list">
                        {category === "freed" ? (
                            <ListItems list={releasedCompanies} />
                        ) : (
                            <ListItems list={stayingCompanies} />
                        )}
                    </ul>
                ) : (
                    <p>Ei vapautuvia yhtiöitä</p>
                )}
            </div>
        </div>
    );

    return (
        <>
            <ResultsList category="freed" />
            <ResultsList category="remaining" />
        </>
    );
};

export default LoadedThirtyYearComparison;
