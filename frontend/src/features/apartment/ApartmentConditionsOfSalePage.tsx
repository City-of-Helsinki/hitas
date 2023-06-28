import {Dispatch, SetStateAction, useEffect, useState} from "react";

import {
    Button,
    Dialog,
    IconArrowLeft,
    IconCross,
    IconCrossCircle,
    IconLock,
    IconLockOpen,
    IconPlus,
    IconPlusCircleFill,
} from "hds-react";
import {Link, useParams} from "react-router-dom";
import {useImmer} from "use-immer";
import {v4 as uuidv4} from "uuid";

import {SerializedError} from "@reduxjs/toolkit";
import {FetchBaseQueryError} from "@reduxjs/toolkit/dist/query/react";
import {
    useCreateConditionOfSaleMutation,
    useGetApartmentDetailQuery,
    useGetOwnersQuery,
    useLazyGetConditionOfSaleQuery,
    useUpdateConditionOfSaleMutation,
} from "../../app/services";
import {FormInputField, Heading, NavigateBackButton, QueryStateHandler, SaveButton} from "../../common/components";
import {IApartmentConditionOfSale, IApartmentDetails, IConditionOfSale, IOwner, IOwnership} from "../../common/schemas";
import {formatAddress, formatDate, formatOwner, hdsToast} from "../../common/utils";
import ApartmentHeader from "./components/ApartmentHeader";

const OwnersList = ({formOwnerList, setFormOwnerList}) => {
    const handleAddOwnerLine = () => {
        setFormOwnerList((draft) => {
            draft.push({key: uuidv4(), ownerId: ""});
        });
    };
    const handleSetOwnerLine = (index) => (value) => {
        setFormOwnerList((draft) => {
            draft[index].ownerId = value;
        });
    };
    const handleRemoveOwnerLine = (index) => {
        setFormOwnerList((draft) => {
            draft.splice(index, 1);
        });
    };

    return (
        <div>
            <ul className="ownership-list">
                <li>
                    <legend className="owner-headings">
                        <span>Omistaja *</span>
                    </legend>
                </li>
                {formOwnerList.map((owner, index) => (
                    <li
                        key={`owner-item-${owner.key}`}
                        className="ownership-item"
                    >
                        <FormInputField
                            inputType="relatedModel"
                            label=""
                            fieldPath="id"
                            queryFunction={useGetOwnersQuery}
                            relatedModelSearchField="name"
                            placeholder={owner?.name || undefined}
                            getRelatedModelLabel={(obj: IOwner) => formatOwner(obj)}
                            formData={formOwnerList[index]}
                            setterFunction={handleSetOwnerLine(index)}
                            error={{}}
                            required
                        />
                        <div className="icon--remove">
                            <IconCrossCircle
                                size="m"
                                onClick={() => handleRemoveOwnerLine(index)}
                            />
                        </div>
                    </li>
                ))}
            </ul>
            <div className="row row--buttons">
                <Button
                    onClick={handleAddOwnerLine}
                    iconLeft={<IconPlus />}
                    variant={formOwnerList.length > 0 ? "secondary" : "primary"}
                    theme="black"
                >
                    Lisää omistaja
                </Button>
            </div>
        </div>
    );
};

const CreateConditionOfSaleModal = ({apartment, isModalOpen, closeModal}) => {
    const initialFormOwnerList = apartment.ownerships.map((o: IOwnership) => {
        return {
            key: uuidv4(),
            ownerId: o.owner.id,
            name: formatOwner(o.owner),
        };
    });
    const [formOwnerList, setFormOwnerList] =
        useImmer<{key: string; ownerId: string; name?: string}[]>(initialFormOwnerList);

    const [createConditionOfSale, {data, error, isLoading}] = useCreateConditionOfSaleMutation();
    const handleCreateConditionOfSale = () => {
        // We need to check if at least one current owner is included in the household.
        // If zero current owners are included, no conditions of sale will be created ever.
        const ownerIdList = formOwnerList.map((o) => o.ownerId);
        const apartmentOwnerIds = apartment.ownerships.map((ownership) => ownership.owner.id);
        if (ownerIdList.some((o) => apartmentOwnerIds.includes(o))) {
            createConditionOfSale({
                data: {household: ownerIdList},
            });
        } else {
            hdsToast.info("Sinun täytyy valita vähintään yksi nykyinen omistaja.");
        }
    };

    useEffect(() => {
        if (isLoading || !data) return;
        if (!error && data) {
            if (data.conditions_of_sale.length) {
                hdsToast.success("Myyntiehdot luotu onnistuneesti.");
                setFormOwnerList(initialFormOwnerList);
            } else {
                hdsToast.info("Yhtään myyntiehtoa ei voitu luoda.");
            }
            closeModal();
        } else {
            hdsToast.error("Myyntiehtojen luonti epäonnistui.");
        }
        // eslint-disable-next-line
    }, [isLoading, error, data]);

    return (
        <Dialog
            id="conditions-of-sale-creation-dialog"
            aria-labelledby="create-modal"
            isOpen={isModalOpen}
            close={() => closeModal()}
            closeButtonLabelText="Sulje"
            boxShadow
        >
            <Dialog.Header
                id="conditions-of-sale-creation-header"
                title="Luo myyntiehto taloudelle"
            />
            <Dialog.Content>
                <OwnersList
                    formOwnerList={formOwnerList}
                    setFormOwnerList={setFormOwnerList}
                />
            </Dialog.Content>
            <Dialog.ActionButtons>
                <Button
                    onClick={() => closeModal()}
                    theme="black"
                    variant="secondary"
                >
                    Peruuta
                </Button>
                <SaveButton
                    onClick={handleCreateConditionOfSale}
                    isLoading={isLoading}
                    disabled={!formOwnerList.length}
                />
            </Dialog.ActionButtons>
        </Dialog>
    );
};

const ExtendGracePeriodModal = ({
    conditionOfSale,
    error,
    isLoading,
    apartmentConditionOfSale,
    isExtendGracePeriodModalOpen,
    closeModal,
}: {
    conditionOfSale: IConditionOfSale;
    error: FetchBaseQueryError | SerializedError | undefined;
    isLoading: boolean;
    apartmentConditionOfSale: IApartmentConditionOfSale;
    isExtendGracePeriodModalOpen: boolean;
    closeModal: () => void;
}) => {
    // Update the conditions of sale object when the update button is clicked
    const [extendGracePeriod, {error: updateError, isLoading: isUpdateLoading}] = useUpdateConditionOfSaleMutation();
    const handleExtendGracePeriod = () => {
        if (conditionOfSale) {
            let updatedConditionOfSale: IConditionOfSale | undefined = undefined;
            switch (conditionOfSale.grace_period) {
                case "not_given":
                    updatedConditionOfSale = {...conditionOfSale, grace_period: "three_months"};
                    break;
                case "three_months":
                    updatedConditionOfSale = {...conditionOfSale, grace_period: "six_months"};
                    break;
            }
            if (updatedConditionOfSale) {
                extendGracePeriod(updatedConditionOfSale)
                    .unwrap()
                    .then(() => {
                        hdsToast.success("Lisäaika myönnetty onnistuneesti!");
                        closeModal();
                    })
                    .catch(() => {
                        hdsToast.error("Virhe lisäajan myöntämisessä! ");
                    });
            } else {
                // if maximum extension has been reached, show error message in the toast and close the modal
                hdsToast.error("Lisäaikaa ei voi enää myöntää!");
                closeModal();
            }
        }
    };

    return (
        <div className="extend-grace-period-modal">
            <Dialog
                id="extend-grace-period-dialog"
                closeButtonLabelText=""
                aria-labelledby=""
                isOpen={isExtendGracePeriodModalOpen}
                close={closeModal}
                boxShadow
            >
                <Dialog.Header
                    id="extend-grace-period-dialog__header"
                    title="Myönnä lisäaikaa"
                />
                <Dialog.Content id="extend-grace-period-dialog__content">
                    <div>
                        {error && "status" in error && "data" in error && (
                            <p className="error-message">
                                Myyntiehtojen hakemisessa tapahtui virhe: {error.status} {JSON.stringify(error.data)}
                            </p>
                        )}
                        {updateError && "status" in updateError && "data" in updateError && (
                            <p className="error-message">
                                Lisäajan tallentamisessa tapahtui virhe: {updateError.status}{" "}
                                {JSON.stringify(updateError.data)}
                            </p>
                        )}
                        <ul className="info-text">
                            <li>
                                <span className="title">Omistaja:</span> {apartmentConditionOfSale.owner.name} (
                                {apartmentConditionOfSale.owner.identifier})
                            </li>
                            <li>
                                <span className="title">Asunto:</span>{" "}
                                {formatAddress(apartmentConditionOfSale.apartment.address)}
                            </li>
                            <li>
                                <span className="title">Myytävä viimeistään: </span>
                                {formatDate(apartmentConditionOfSale.sell_by_date)}
                            </li>
                        </ul>
                        {apartmentConditionOfSale.grace_period === "not_given" && (
                            <p>Lisäaikaa ei ole vielä myönnetty. Myönnetäänkö 3kk lisäaikaa asunnon myyntiehtoon? </p>
                        )}
                        {apartmentConditionOfSale.grace_period === "three_months" && (
                            <p>Lisäaikaa on jo myönnetty 3kk. Myönnetäänkö 3kk lisää aikaa asunnon myyntiehtoon?</p>
                        )}
                        {apartmentConditionOfSale.grace_period === "six_months" && (
                            <p>Lisäaikaa asunnon myyntiehtoon on jo myönnetty 6kk, enempää ei voi myöntää.</p>
                        )}
                    </div>
                </Dialog.Content>
                <Dialog.ActionButtons>
                    <Button
                        theme="black"
                        iconLeft={<IconArrowLeft />}
                        variant="secondary"
                        onClick={closeModal}
                    >
                        Peruuta
                    </Button>

                    <SaveButton
                        onClick={handleExtendGracePeriod}
                        buttonText="Hyväksy"
                        isLoading={isLoading || isUpdateLoading}
                        disabled={!!error || isLoading || isUpdateLoading}
                    />
                </Dialog.ActionButtons>{" "}
            </Dialog>
        </div>
    );
};

const ExtendGracePeriodButton = ({handleExtendGracePeriodButtonClick, setIsHoverExtendGracePeriodButton}) => {
    return (
        <button
            className="text-button"
            onClick={handleExtendGracePeriodButtonClick}
        >
            <IconPlusCircleFill
                className="icon"
                aria-label="Myönnä lisäaikaa"
                onMouseEnter={() => setIsHoverExtendGracePeriodButton(true)}
                onMouseLeave={() => setIsHoverExtendGracePeriodButton(false)}
            />
        </button>
    );
};

const GracePeriodEntry = ({
    apartmentConditionOfSale,
    setIsHoverExtendGracePeriodButton,
}: {
    apartmentConditionOfSale: IApartmentConditionOfSale;
    setIsHoverExtendGracePeriodButton: Dispatch<SetStateAction<boolean>>;
}) => {
    // Handle the visibility of the modal
    const [isExtendGracePeriodModalOpen, setIsExtendGracePeriodModalOpen] = useState<boolean>(false);
    const closeModal = () => {
        setIsExtendGracePeriodModalOpen(false);
        setIsHoverExtendGracePeriodButton(false);
    };

    // Get the corresponding conditions of sale object when the extend grace period button is clicked
    const [getConditionOfSale, {data: conditionOfSale, error, isLoading}] = useLazyGetConditionOfSaleQuery();
    const handleExtendGracePeriodButtonClick = () => {
        getConditionOfSale(apartmentConditionOfSale.id);
        setIsExtendGracePeriodModalOpen(true);
    };

    // booleans to determine the grace period entry
    const hasThreeMonthsGracePeriod = apartmentConditionOfSale.grace_period === "three_months";
    const hasSixMonthsGracePeriod = apartmentConditionOfSale.grace_period === "six_months";
    const hasNoGracePeriod =
        apartmentConditionOfSale.grace_period === "not_given" ||
        (!hasThreeMonthsGracePeriod && !hasSixMonthsGracePeriod);

    return (
        <>
            {hasNoGracePeriod && <IconCross />}
            {hasThreeMonthsGracePeriod && <span>3kk</span>}
            {hasSixMonthsGracePeriod && <span>6kk</span>}
            {(hasNoGracePeriod || hasThreeMonthsGracePeriod) && (
                <ExtendGracePeriodButton {...{handleExtendGracePeriodButtonClick, setIsHoverExtendGracePeriodButton}} />
            )}
            <ExtendGracePeriodModal
                conditionOfSale={conditionOfSale as IConditionOfSale}
                {...{
                    error,
                    isLoading,
                    apartmentConditionOfSale,
                    isExtendGracePeriodModalOpen,
                    closeModal,
                }}
            />
        </>
    );
};

const ConditionsOfSaleList = ({apartment}: {apartment: IApartmentDetails}) => {
    const [isHoverExtendGracePeriodButton, setIsHoverExtendGracePeriodButton] = useState(false);
    return (
        <>
            {apartment.conditions_of_sale.length ? (
                <ul className="conditions-of-sale-list">
                    <li className="conditions-of-sale-headers">
                        <header>Omistaja</header>
                        <header>Asunto</header>
                        <header>{isHoverExtendGracePeriodButton ? "Myönnä lisäaikaa" : "Lisäaika"}</header>
                        <header>Myytävä viimeistään</header>
                        <header>Toteutunut</header>
                    </li>
                    {apartment.conditions_of_sale.map((cos: IApartmentConditionOfSale) => (
                        <li
                            key={`conditions-of-sale-item-${cos.id}`}
                            className={`conditions-of-sale-list-item${cos.fulfilled ? " resolved" : " unresolved"}`}
                        >
                            <div className="input-wrap">
                                <div className="icon-wrap">{cos.fulfilled ? <IconLockOpen /> : <IconLock />}</div>
                                {cos.owner.name} ({cos.owner.identifier})
                            </div>
                            <div className="input-wrap">
                                <Link
                                    to={`/housing-companies/${cos.apartment.housing_company.id}/apartments/${cos.apartment.id}`}
                                >
                                    {formatAddress(cos.apartment.address)}
                                </Link>
                            </div>
                            <div className="input-wrap grace-period">
                                <GracePeriodEntry
                                    setIsHoverExtendGracePeriodButton={setIsHoverExtendGracePeriodButton}
                                    apartmentConditionOfSale={cos}
                                />
                            </div>
                            <div className="input-wrap sell-by-date">{formatDate(cos.sell_by_date)} </div>
                            <div className="input-wrap fulfillment-date">{formatDate(cos.fulfilled)} </div>
                        </li>
                    ))}
                </ul>
            ) : (
                <div>Ei myyntiehtoja</div>
            )}
        </>
    );
};

const ApartmentConditionsOfSalePage = () => {
    const params = useParams();
    const {data, error, isLoading} = useGetApartmentDetailQuery({
        housingCompanyId: params.housingCompanyId as string,
        apartmentId: params.apartmentId as string,
    });
    const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

    return (
        <div className="view--create view--apartment-conditions-of-sale">
            <ApartmentHeader />
            <Heading type="main">Myyntiehdot</Heading>
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <ConditionsOfSaleList apartment={data as IApartmentDetails} />
                <div className="row row--buttons">
                    <NavigateBackButton />
                    <Button
                        theme="black"
                        iconLeft={<IconPlus />}
                        onClick={() => setIsModalOpen(true)}
                    >
                        Lisää uusi
                    </Button>
                </div>
                <CreateConditionOfSaleModal
                    apartment={data as IApartmentDetails}
                    isModalOpen={isModalOpen}
                    closeModal={() => {
                        setIsModalOpen(false);
                    }}
                />
            </QueryStateHandler>
        </div>
    );
};

export default ApartmentConditionsOfSalePage;
