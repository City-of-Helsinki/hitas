import {Button, IconCrossCircle, IconPlus, IconSearch, TextInput} from "hds-react";
import {useCallback, useRef, useState} from "react";
import {useGetPropertyManagersQuery} from "../../app/services";
import {ModifyManagerModal, QueryStateHandler} from "../../common/components";
import {IFilterManagersQuery, IPropertyManager} from "../../common/schemas";

const ManagerResultList: React.FC<{params: IFilterManagersQuery}> = ({params}) => {
    const MIN_LENGTH = 2; // Minimum length before applying filter
    const MAX_ROWS = 12; // Maximum rows to show
    if (params.name?.length && params.name?.length < MIN_LENGTH) {
        delete params.name;
    }
    if (params.email?.length && params.email?.length < MIN_LENGTH) {
        delete params.email;
    }
    // get the data
    const {data, error, isLoading} = useGetPropertyManagersQuery({...params, limit: MAX_ROWS});

    // state for the modals
    const [isModifyManagerModalOpen, setIsModifyManagerModalOpen] = useState(false);
    const [isAddNewManagerModalOpen, setIsAddNewManagerModalOpen] = useState(false);
    const [manager, setManager] = useState<IPropertyManager | undefined>(undefined);

    // action for the row click
    const editFn = (managerEdited: IPropertyManager) => {
        setIsModifyManagerModalOpen(true);
        setManager(managerEdited);
    };
    return (
        <QueryStateHandler
            data={data}
            error={error}
            isLoading={isLoading}
        >
            <div className="list-headers">
                <div>Nimi</div>
                <div>Sähköpostiosoite</div>
            </div>
            <ul className="results-list">
                {data?.contents.map((manager: IPropertyManager) => (
                    <div
                        key={manager.id}
                        className="results-list__item"
                        onClick={(e) => {
                            e.preventDefault();
                            editFn(manager);
                        }}
                    >
                        <span>{manager.name}</span>
                        <span>{manager.email}</span>
                    </div>
                ))}
            </ul>
            <div className="list-footer">
                <div className="list-footer-item">
                    Näytetään {data?.page.size}/{data?.page.total_items} hakutulosta
                </div>
                <div className="list-footer-item">
                    <Button
                        theme="black"
                        iconLeft={<IconPlus />}
                        onClick={() => setIsAddNewManagerModalOpen(true)}
                    >
                        Luo uusi
                    </Button>
                </div>
            </div>
            <ModifyManagerModal
                manager={manager as IPropertyManager}
                isVisible={isModifyManagerModalOpen}
                setIsVisible={setIsModifyManagerModalOpen}
            />
            <ModifyManagerModal
                isVisible={isAddNewManagerModalOpen}
                setIsVisible={setIsAddNewManagerModalOpen}
            />
        </QueryStateHandler>
    );
};

export default function ManagersList() {
    // search strings
    const [filterParams, setFilterParams] = useState<IFilterManagersQuery>({name: "", email: ""});

    // focus the field when clicking its cross circle icon
    const nameSearchRef = useRef<HTMLInputElement>(null);
    const emailSearchRef = useRef<HTMLInputElement>(null);
    const focus = useCallback(
        (field: string) => {
            if (field === "name") {
                nameSearchRef.current?.focus();
            } else if (field === "email") {
                emailSearchRef.current?.focus();
            }
        },
        [nameSearchRef, emailSearchRef]
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
                    id="filter__email"
                    ref={emailSearchRef}
                    label="Sähköpostiosoite"
                    value={filterParams.email}
                    onChange={(e) => setFilterParams((prev) => ({...prev, email: e.target.value}))}
                    onButtonClick={() => clearAndFocus("email")}
                    buttonIcon={filterParams.email ? <IconCrossCircle /> : <IconSearch />}
                />
            </div>
            <ManagerResultList params={filterParams} />
        </div>
    );
}
