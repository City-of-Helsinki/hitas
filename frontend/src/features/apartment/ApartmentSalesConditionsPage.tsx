import React, {useEffect, useState} from "react";

import {Button, Dialog, IconCrossCircle, IconLock, IconLockOpen, IconPlus} from "hds-react";
import {Link, useParams} from "react-router-dom";
import {useImmer} from "use-immer";
import {v4 as uuidv4} from "uuid";

import {useCreateConditionOfSaleMutation, useGetApartmentDetailQuery, useGetOwnersQuery} from "../../app/services";
import {FormInputField, Heading, NavigateBackButton, QueryStateHandler, SaveButton} from "../../common/components";
import {IApartmentConditionOfSale, IApartmentDetails, IOwner, IOwnership} from "../../common/schemas";
import {formatAddress, formatDate, formatOwner, hitasToast} from "../../common/utils";
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
                    Valitse omistaja
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
            hitasToast("Sinun täytyy valita vähintään yksi nykyinen omistaja.", "info");
        }
    };

    useEffect(() => {
        if (isLoading || !data) return;
        if (!error && data) {
            if (data.conditions_of_sale.length) {
                hitasToast("Myyntiehdot luotu onnistuneesti.", "success");
                setFormOwnerList(initialFormOwnerList);
            } else {
                hitasToast("Yhtään myyntiehtoa ei voitu luoda.", "info");
            }
            closeModal();
        } else {
            hitasToast("Myyntiehtojen luonti epäonnistui.", "error");
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

const SalesConditionsList = ({apartment}: {apartment: IApartmentDetails}) => {
    return (
        <>
            {apartment.conditions_of_sale.length ? (
                <>
                    <li className="conditions-of-sale-headers">
                        <header>Omistaja</header>
                        <header>Asunto</header>
                        <header>Lisäaika</header>
                        <header>Toteutunut</header>
                    </li>
                    {apartment.conditions_of_sale.map((cos: IApartmentConditionOfSale) => (
                        <li
                            key={`conditions-of-sale-item-${cos.id}`}
                            className={`conditions-of-sale-list-item${cos.fulfilled ? " resolved" : " unresolved"}`}
                        >
                            <div className="input-wrap">
                                {cos.fulfilled ? <IconLockOpen /> : <IconLock />}
                                {cos.owner.name} ({cos.owner.identifier})
                            </div>
                            <div className="input-wrap">
                                <Link
                                    to={`/housing-companies/${cos.apartment.housing_company.id}/apartments/${cos.apartment.id}`}
                                >
                                    {formatAddress(cos.apartment.address)}
                                </Link>
                            </div>
                            <div className="input-wrap">{cos.grace_period}</div>
                            <div className="input-wrap">{formatDate(cos.fulfilled)} </div>
                        </li>
                    ))}
                </>
            ) : (
                <div>Ei myyntiehtoja</div>
            )}
        </>
    );
};

const ApartmentSalesConditionsPage = () => {
    const params = useParams();
    const {data, error, isLoading} = useGetApartmentDetailQuery({
        housingCompanyId: params.housingCompanyId as string,
        apartmentId: params.apartmentId as string,
    });
    const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

    return (
        <div className="view--create view--apartment-conditions-of-sale">
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <ApartmentHeader apartment={data as IApartmentDetails} />
            </QueryStateHandler>
            <Heading type="main">Myyntiehdot</Heading>
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                <ul className="conditions-of-sale-list">
                    <SalesConditionsList apartment={data as IApartmentDetails} />
                </ul>
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

export default ApartmentSalesConditionsPage;
