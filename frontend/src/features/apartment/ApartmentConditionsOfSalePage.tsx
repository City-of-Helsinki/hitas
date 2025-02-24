import {useContext, useRef, useState} from "react";

import {Button, IconCrossCircle, IconLock, IconPlus, IconPlusCircleFill, IconTrash, Table} from "hds-react";
import {Link} from "react-router-dom";

import {useFieldArray, useForm, useFormContext} from "react-hook-form";
import {DeleteButton, GenericActionModal, Heading, NavigateBackButton, SaveButton} from "../../common/components";
import {FormProviderForm, RelatedModelInput, SaveFormButton} from "../../common/components/forms";
import {getConditionOfSaleGracePeriodLabel} from "../../common/localisation";
import {IApartmentConditionOfSale, IOwner, IOwnership} from "../../common/schemas";
import {
    useCreateConditionOfSaleMutation,
    useDeleteConditionOfSaleMutation,
    useGetOwnersQuery,
    usePatchConditionOfSaleMutation,
} from "../../common/services";
import {tableThemeEngel} from "../../common/themes";
import {formatAddress, formatApartmentAddressShort, formatDate, formatOwner, hdsToast} from "../../common/utils";
import {ApartmentViewContext, ApartmentViewContextProvider} from "./components/ApartmentViewContextProvider";
import ConditionsOfSaleStatus from "./components/ConditionsOfSaleStatus";

const HouseholdOwnersList = () => {
    const formObject = useFormContext();

    const {fields, append, remove} = useFieldArray({
        name: "household",
        control: formObject.control,
    });
    formObject.register("household");
    const household = formObject.watch("household");

    const addEmptyLine = () => {
        append(null as unknown as IOwner);
    };

    return (
        <div>
            <ul className="ownership-list">
                <li>
                    <legend className="owner-headings">
                        <span>Omistaja *</span>
                    </legend>
                </li>
                {fields.map((field, index) => (
                    <li
                        key={`owner-item-${field.id}`}
                        className="ownership-item"
                    >
                        <RelatedModelInput
                            label="Omistaja"
                            queryFunction={useGetOwnersQuery}
                            relatedModelSearchField="name"
                            name={`household.${index}.owner`}
                            transform={(obj) => formatOwner(obj)}
                            required
                        />
                        <div className="icon--remove">
                            <span onClick={() => remove(index)}>
                                <IconCrossCircle size="m" />
                            </span>
                        </div>
                    </li>
                ))}
            </ul>
            <div className="row row--buttons">
                <Button
                    iconLeft={<IconPlus />}
                    variant={household.length > 0 ? "secondary" : "primary"}
                    theme="black"
                    onClick={addEmptyLine}
                >
                    Lisää omistaja
                </Button>
            </div>
        </div>
    );
};

const DuplicateConditionsOfSaleHelpText = ({apartment, formObject}) => {
    // Display a warning message, that if user creates a new condition of sale to an apartment that has at least 2
    // owners and the household includes at least one owner not in the apartment, the conditions of sale will look
    // like duplicates.
    // This is due to the new conditions of sale having the same owner and apartment, but in truth they are
    // different conditions of sale, because they are linked to different owners in this apartment.

    // No need to show warning when apartment has less than 2 owners
    if (apartment.ownerships.length < 2) return null;

    const household = formObject.watch("household").filter((o) => o?.owner?.id);
    const apartmentOwnerIds = apartment.ownerships.map((o) => o.owner.id);
    const householdOtherOwnersCount = household.filter((o) => !apartmentOwnerIds.includes(o?.owner?.id)).length;
    // No need to show warning when household includes only owners in this apartment
    if (householdOtherOwnersCount < 1) return null;
    // No need to show warning when user selected only one current owner
    if (household.length - householdOtherOwnersCount < 2) return null;

    return (
        <p className="help-text">
            Huom! Taloudelle luotavat myyntiehdot voivat näyttää duplikaateilta, koska niissä on sama toinen omistaja.
            Myyntiehdot ovat kuitenkin toisistaan erillisiä, sillä ne kohdistuvat tämän asunnon eri omistajiin.
        </p>
    );
};

const CreateConditionOfSaleButton = () => {
    const {apartment} = useContext(ApartmentViewContext);
    if (!apartment) throw new Error("Apartment not found");

    const [isModalOpen, setIsModalOpen] = useState(false);
    const closeModal = () => setIsModalOpen(false);

    const initialFormOwnerList: {owner: IOwner}[] = apartment.ownerships.map((o: IOwnership) => {
        return {owner: o.owner};
    });

    const formRef = useRef<HTMLFormElement>(null);
    const formObject = useForm({
        defaultValues: {household: initialFormOwnerList},
        mode: "all",
    });

    const [createConditionOfSale, {isLoading}] = useCreateConditionOfSaleMutation();

    const handleCreateConditionOfSale = (data) => {
        // We need to check if at least one current owner is included in the household.
        // If zero current owners are included, no conditions of sale will be created ever.
        const householdOwnerIds = data.household.filter((o) => o.owner.id).map((o) => o.owner.id);
        const apartmentOwnerIds = apartment.ownerships.map((ownership) => ownership.owner.id);

        if (householdOwnerIds.some((o) => apartmentOwnerIds.includes(o))) {
            createConditionOfSale({
                data: {household: householdOwnerIds},
            })
                .unwrap()
                .then((payload) => {
                    if (payload.conditions_of_sale.length) {
                        hdsToast.success("Myyntiehdot luotu onnistuneesti.");
                    } else {
                        hdsToast.info("Yhtään myyntiehtoa ei voitu luoda.");
                    }
                    closeModal();
                    formObject.reset();
                })
                .catch(() => {
                    hdsToast.error("Myyntiehtojen luonti epäonnistui!");
                });
        } else {
            hdsToast.info("Sinun täytyy valita vähintään yksi nykyinen omistaja.");
        }
    };

    return (
        <>
            <Button
                theme="black"
                iconLeft={<IconPlus />}
                onClick={() => setIsModalOpen(true)}
            >
                Lisää uusi
            </Button>

            <GenericActionModal
                id="conditions-of-sale-creation-dialog"
                title="Luo myyntiehto taloudelle"
                modalIcon={<IconLock />}
                isModalOpen={isModalOpen}
                closeModal={closeModal}
                confirmButton={
                    <SaveFormButton
                        formRef={formRef}
                        isLoading={isLoading}
                        disabled={!formObject.getValues("household").length}
                    />
                }
            >
                <FormProviderForm
                    formObject={formObject}
                    formRef={formRef}
                    onSubmit={handleCreateConditionOfSale}
                >
                    <HouseholdOwnersList />
                </FormProviderForm>
                <DuplicateConditionsOfSaleHelpText
                    apartment={apartment}
                    formObject={formObject}
                />
            </GenericActionModal>
        </>
    );
};

const ConditionOfSaleGracePeriodButton = ({conditionOfSale}: {conditionOfSale: IApartmentConditionOfSale}) => {
    const [isModalOpen, setIsModalOpen] = useState(false);

    const closeModal = () => setIsModalOpen(false);

    const [patchConditionOfSale, {error, isLoading}] = usePatchConditionOfSaleMutation();

    const handleExtendGracePeriod = () => {
        const patchData = {
            id: conditionOfSale.id,
            grace_period: conditionOfSale.grace_period === "not_given" ? "three_months" : "six_months",
        } as Partial<IApartmentConditionOfSale>;

        patchConditionOfSale(patchData)
            .unwrap()
            .then(() => {
                hdsToast.success("Lisäaika myönnetty onnistuneesti!");
                closeModal();
            })
            .catch(() => {
                hdsToast.error("Virhe lisäajan myöntämisessä!");
            });
    };

    return (
        <>
            <button
                title="Myönnä lisäaikaa"
                className="text-button"
                onClick={() => setIsModalOpen(true)}
            >
                <IconPlusCircleFill
                    className="icon"
                    aria-label="Myönnä lisäaikaa"
                />
            </button>

            <GenericActionModal
                title="Myönnä lisäaikaa"
                modalIcon={<IconLock />}
                isModalOpen={isModalOpen}
                closeModal={closeModal}
                confirmButton={
                    <SaveButton
                        onClick={handleExtendGracePeriod}
                        buttonText="Hyväksy"
                        isLoading={isLoading}
                        disabled={!!error}
                    />
                }
            >
                {error && "status" in error && "data" in error && (
                    <p className="error-message">
                        Lisäajan tallentamisessa tapahtui virhe: {error.status} {JSON.stringify(error.data)}
                    </p>
                )}
                <ul className="info-text">
                    <li>
                        <span className="title">Omistaja:</span> {formatOwner(conditionOfSale.owner)}
                    </li>
                    <li>
                        <span className="title">Asunto:</span> {formatAddress(conditionOfSale.apartment.address)}
                    </li>
                    <li>
                        <span className="title">Myytävä viimeistään: </span> {formatDate(conditionOfSale.sell_by_date)}
                    </li>
                </ul>
                {conditionOfSale.grace_period === "not_given" && (
                    <p>
                        Asunnolle '{formatAddress(conditionOfSale.apartment.address)}' ei ole vielä myönnetty lisäaikaa.
                        Myönnetäänkö 3kk lisäaikaa asunnon myymiseen?
                    </p>
                )}
                {conditionOfSale.grace_period === "three_months" && (
                    <p>
                        Asunnolle '{formatAddress(conditionOfSale.apartment.address)}' on jo myönnetty 3kk lisäaikaa.
                        Myönnetäänkö vielä 3kk lisäaikaa asunnon myymiseen?
                    </p>
                )}
                {conditionOfSale.grace_period === "six_months" && (
                    <p>Lisäaikaa asunnon myymiseen on jo myönnetty 6kk, enempää ei voi myöntää.</p>
                )}
            </GenericActionModal>
        </>
    );
};

const DeleteConditionOfSaleButton = ({conditionOfSale}: {conditionOfSale: IApartmentConditionOfSale}) => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const closeModal = () => setIsModalOpen(false);

    const [deleteConditionOfSale, {isLoading}] = useDeleteConditionOfSaleMutation();

    const handleDeleteConditionOfSale = () => {
        deleteConditionOfSale({id: conditionOfSale.id})
            .unwrap()
            .then(() => {
                hdsToast.info("Myyntiehto poistettu onnistuneesti.");
                setIsModalOpen(false);
            })
            .catch((e) => {
                hdsToast.error("Myyntiehdon poistaminen epäonnistui!");
                // eslint-disable-next-line no-console
                console.warn(e);
            });
    };

    return (
        <>
            <DeleteButton
                onClick={() => setIsModalOpen(true)}
                isLoading={isLoading}
                size="small"
            />
            <GenericActionModal
                title="Poista myyntiehto"
                modalIcon={<IconTrash />}
                isModalOpen={isModalOpen}
                closeModal={closeModal}
                confirmButton={
                    <DeleteButton
                        onClick={handleDeleteConditionOfSale}
                        isLoading={isLoading}
                    />
                }
            >
                <p>
                    Oletko varma, että haluat poistaa henkilön '{formatOwner(conditionOfSale.owner)}' myyntiehdon
                    asuntoon '{formatAddress(conditionOfSale.apartment.address)}'?
                </p>
            </GenericActionModal>
        </>
    );
};

const getConditionsOfSaleTableColumns = () => {
    return [
        {
            key: "stair",
            headerName: "Omistaja",
            transform: (obj) => (
                <div className={`row${obj.fulfilled ? " fulfilled" : ""}`}>
                    <div>
                        <ConditionsOfSaleStatus
                            conditionOfSale={obj}
                            withSellByDate={false}
                        />
                    </div>
                    <div>
                        <b>{obj.owner.name}</b>
                        {obj.owner.identifier ? (
                            <>
                                <br />
                                {obj.owner.identifier}
                            </>
                        ) : null}
                    </div>
                </div>
            ),
        },
        {
            key: "apartment",
            headerName: "Asunto",
            transform: (obj) => (
                <div className={`${obj.fulfilled ? " fulfilled" : ""}`}>
                    <b>{obj.apartment.housing_company.display_name}</b>
                    <Link to={`/housing-companies/${obj.apartment.housing_company.id}/apartments/${obj.apartment.id}`}>
                        <br />
                        {formatApartmentAddressShort(obj.apartment.address)}
                    </Link>
                </div>
            ),
        },
        {
            key: "grace_period",
            headerName: "Lisäaika",
            transform: (obj) => (
                <div className={`row${obj.fulfilled ? " fulfilled" : ""}`}>
                    <span>{getConditionOfSaleGracePeriodLabel(obj)}</span>
                    {obj.grace_period !== "six_months" && !obj.fulfilled ? (
                        <ConditionOfSaleGracePeriodButton conditionOfSale={obj} />
                    ) : (
                        ""
                    )}
                </div>
            ),
        },
        {
            key: "sell_by_date",
            headerName: "Myytävä viimeistään",
            transform: (obj) => (
                <div className={`text-right${obj.fulfilled ? " fulfilled" : ""}`}>{formatDate(obj.sell_by_date)}</div>
            ),
        },
        {
            key: "fulfilled",
            headerName: "Toteutunut",
            transform: (obj) => <div className="text-right">{formatDate(obj.fulfilled)}</div>,
        },
        {
            key: "delete",
            headerName: "",
            transform: (obj) => <DeleteConditionOfSaleButton conditionOfSale={obj} />,
        },
    ];
};

const LoadedConditionsOfSalePage = () => {
    const {apartment} = useContext(ApartmentViewContext);
    if (!apartment) throw new Error("Apartment not found");

    return (
        <>
            <Heading type="main">Myyntiehdot</Heading>
            <div className="conditions-of-sale-table">
                {apartment.conditions_of_sale.length ? (
                    <Table
                        id="conditions-of-sale-table"
                        cols={getConditionsOfSaleTableColumns()}
                        rows={apartment.conditions_of_sale}
                        indexKey="id"
                        variant="light"
                        theme={tableThemeEngel}
                        dense
                        zebra
                    />
                ) : (
                    <div>Ei myyntiehtoja</div>
                )}
            </div>
            <div className="row row--buttons">
                <NavigateBackButton />
                <CreateConditionOfSaleButton />
            </div>
        </>
    );
};

const ApartmentConditionsOfSalePage = () => {
    return (
        <ApartmentViewContextProvider viewClassName="view--create view--apartment-conditions-of-sale">
            <LoadedConditionsOfSalePage />
        </ApartmentViewContextProvider>
    );
};

export default ApartmentConditionsOfSalePage;
