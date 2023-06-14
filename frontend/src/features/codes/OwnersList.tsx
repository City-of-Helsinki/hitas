import {IconCrossCircle, IconSearch, TextInput} from "hds-react";
import {useCallback, useRef, useState} from "react";
import {useGetOwnersQuery} from "../../app/services";
import {ModifyOwnerModal, QueryStateHandler} from "../../common/components";
import {IFilterOwnersQuery, IOwner} from "../../common/schemas";

const OwnerResultList: React.FC<{params: IFilterOwnersQuery}> = ({params}) => {
    const MIN_LENGTH = 2; // Minimum length before applying filter
    const MAX_ROWS = 12; // Maximum rows to show
    if (params.name?.length && params.name?.length < MIN_LENGTH) {
        delete params.name;
    }
    if (params.identifier?.length && params.identifier?.length < MIN_LENGTH) {
        delete params.identifier;
    }
    // get the data
    const {data, error, isLoading} = useGetOwnersQuery({...params, limit: MAX_ROWS});

    // state for the modal
    const [isModifyOwnerModalOpen, setIsModifyOwnerModalOpen] = useState(false);
    const [owner, setOwner] = useState<IOwner | undefined>(undefined);

    // action for the row click
    const editFn = (ownerEdited: IOwner) => {
        setIsModifyOwnerModalOpen(true);
        setOwner(ownerEdited);
    };
    return (
        <QueryStateHandler
            data={data}
            error={error}
            isLoading={isLoading}
        >
            <div className="list-headers">
                <div>Nimi</div>
                <div>Henkilö- tai Y-tunnus</div>
            </div>
            <ul className="results-list">
                {data?.contents.map((owner: IOwner) => (
                    <div
                        key={owner.id}
                        className="results-list__item"
                        onClick={(e) => {
                            e.preventDefault();
                            editFn(owner);
                        }}
                    >
                        <span>{owner.name}</span>
                        <span>{owner.identifier}</span>
                    </div>
                ))}
            </ul>
            <div className="list-footer">
                <div className="list-footer-item">
                    Näytetään {data?.page.size}/{data?.page.total_items} hakutulosta
                </div>
            </div>
            <ModifyOwnerModal
                owner={owner as IOwner}
                isVisible={isModifyOwnerModalOpen}
                setIsVisible={setIsModifyOwnerModalOpen}
            />
        </QueryStateHandler>
    );
};

export default function OwnersList() {
    // search strings
    const [filterParams, setFilterParams] = useState<IFilterOwnersQuery>({name: "", identifier: ""});

    // focus the field when clicking its cross circle icon
    const nameSearchRef = useRef<HTMLInputElement>(null);
    const identifierSearchRef = useRef<HTMLInputElement>(null);
    const focus = useCallback(
        (field: string) => {
            if (field === "name") {
                nameSearchRef.current?.focus();
            } else if (field === "identifier") {
                identifierSearchRef.current?.focus();
            }
        },
        [nameSearchRef, identifierSearchRef]
    );
    const clearAndFocus = (field: string) => {
        setFilterParams((prev) => ({...prev, [field]: ""}));
        focus(field);
    };

    return (
        <div className="listing">
            <div className="filters">
                <TextInput
                    id="filter__name"
                    ref={nameSearchRef}
                    label="Nimi"
                    value={filterParams.name}
                    onChange={(e) => setFilterParams((prev) => ({...prev, name: e.target.value}))}
                    onButtonClick={() => clearAndFocus("name")}
                    autoFocus
                    buttonIcon={filterParams.name ? <IconCrossCircle /> : <IconSearch />}
                />
                <TextInput
                    id="filter__identifier"
                    ref={identifierSearchRef}
                    label="Henkilö- tai Y-tunnus"
                    value={filterParams.identifier}
                    onChange={(e) => setFilterParams((prev) => ({...prev, identifier: e.target.value}))}
                    onButtonClick={() => clearAndFocus("identifier")}
                    buttonIcon={filterParams.identifier ? <IconCrossCircle /> : <IconSearch />}
                />
            </div>
            <OwnerResultList params={filterParams} />
        </div>
    );
}
