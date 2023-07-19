import {useContext, useRef, useState} from "react";

import {Button, IconCrossCircle, IconLock, IconPlus, IconPlusCircleFill, Table} from "hds-react";
import {Link} from "react-router-dom";

import {useFieldArray, useForm, useFormContext} from "react-hook-form";
import {
    useCreateConditionOfSaleMutation,
    useDeleteConditionOfSaleMutation,
    useGetOwnersQuery,
    usePatchConditionOfSaleMutation,
} from "../../app/services";
import {
    ConfirmDialogModal,
    GenericActionModal,
    Heading,
    NavigateBackButton,
    RemoveButton,
    SaveButton,
} from "../../common/components";
import {FormProviderForm, RelatedModelInput, SaveFormButton} from "../../common/components/forms";
import {getConditionOfSaleGracePeriodLabel} from "../../common/localisation";
import {IApartmentConditionOfSale, IApartmentDetails, IOwner, IOwnership} from "../../common/schemas";
import {formatAddress, formatDate, formatOwner, hdsToast} from "../../common/utils";
import {ApartmentViewContext, ApartmentViewContextProvider} from "./components/ApartmentViewContextProvider";
import ConditionsOfSaleStatus from "./components/ConditionsOfSaleStatus";

const tableTheme = {
    "--header-background-color": "var(--color-engel-medium-light)",
};

const HouseholdOwnersList = () => {
    const formObject = useFormContext();

    const {fields, append, remove} = useFieldArray({
        name: "household",
        control: formObject.control,
    });
    formObject.register("household");
    const household = formObject.watch("household");

    // Blank Ownership. This is appended to the list when user clicks "New ownership"
    const emptyOwner = {owner: {id: ""} as IOwner};

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
                            formatFormObjectValue={(obj) => formatOwner(obj)}
                            required
                        />
                        <div className="icon--remove">
                            <IconCrossCircle
                                size="m"
                                onClick={() => remove(index)}
                            />
                        </div>
                    </li>
                ))}
            </ul>
            <div className="row row--buttons">
                <Button
                    iconLeft={<IconPlus />}
                    variant={household.length > 0 ? "secondary" : "primary"}
                    theme="black"
                    onClick={() => append(emptyOwner)}
                >
                    Lisää omistaja
                </Button>
            </div>
        </div>
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

    const [deleteConditionOfSale, {data, error, isLoading}] = useDeleteConditionOfSaleMutation();

    const handleDeleteConditionOfSale = () => {
        deleteConditionOfSale({id: conditionOfSale.id})
            .unwrap()
            .then(() => {
                hdsToast.success("Myyntiehto poistettu onnistuneesti.");
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
            <RemoveButton
                onClick={() => setIsModalOpen(true)}
                isLoading={isLoading}
                size="small"
                buttonText="Poista"
            />
            <ConfirmDialogModal
                data={data}
                error={error}
                isLoading={isLoading}
                isVisible={isModalOpen}
                setIsVisible={setIsModalOpen}
                modalHeader="Poista myyntiehto"
                modalText={`Oletko varma, että haluat poistaa henkilön '${formatOwner(
                    conditionOfSale.owner
                )}' myyntiehdon asuntoon '${formatAddress(conditionOfSale.apartment.address)}'?`}
                buttonText="Poista"
                confirmAction={handleDeleteConditionOfSale}
                cancelAction={() => setIsModalOpen(false)}
            />
        </>
    );
};

const getConditionsOfSaleTableColumns = (apartment: IApartmentDetails) => {
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
                    {formatOwner(obj.owner)}
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
                        {formatAddress(obj.apartment.address)}
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
            transform: (obj) =>
                !apartment.ownerships.find((ownership) => ownership.owner.id === obj.owner.id) && !obj.fulfilled ? (
                    <DeleteConditionOfSaleButton conditionOfSale={obj} />
                ) : (
                    ""
                ),
        },
    ];
};

const LoadedConditionsOfSalePage = () => {
    const {apartment} = useContext(ApartmentViewContext);
    if (!apartment) throw new Error("Apartment not found");

    if (!apartment.conditions_of_sale.length) {
        return <div>Ei myyntiehtoja</div>;
    }

    return (
        <>
            <Heading type="main">Myyntiehdot</Heading>
            <div className="conditions-of-sale-table">
                <Table
                    id="conditions-of-sale-table"
                    cols={getConditionsOfSaleTableColumns(apartment)}
                    rows={apartment.conditions_of_sale}
                    indexKey="id"
                    variant="light"
                    theme={tableTheme}
                    dense
                    zebra
                />
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
