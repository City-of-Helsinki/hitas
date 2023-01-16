import React from "react";

import {Button, IconAlertCircleFill, IconCrossCircle, IconPlus} from "hds-react";
import {v4 as uuidv4} from "uuid";

import {useGetOwnersQuery} from "../../app/services";
import {IOwner, IOwnership} from "../models";
import {dotted, formatOwner} from "../utils";
import {FormInputField} from "./index";

const OwnershipsList = ({apartment, formOwnershipsList, setFormOwnershipsList}) => {
    const error = {};

    // Ownerships
    const handleAddOwnershipLine = () => {
        setFormOwnershipsList((draft) => {
            draft.push({
                key: uuidv4(),
                owner: {id: ""} as IOwner,
                percentage: 100,
            });
        });
    };
    const handleSetOwnershipLine = (index, fieldPath) => (value) => {
        setFormOwnershipsList((draft) => {
            dotted(draft[index], fieldPath, value);
        });
    };
    const handleRemoveOwnershipLine = (index) => {
        setFormOwnershipsList((draft) => {
            draft.splice(index, 1);
        });
    };
    const getOwnershipPercentageError = (error) => {
        if (
            error &&
            error?.data?.fields &&
            error.data.fields.filter((e) => e.field === "ownerships.percentage").length
        ) {
            return error.data.fields.filter((e) => e.field === "ownerships.percentage")[0].message;
        }
        return "";
    };

    return (
        <>
            <ul className="ownerships-list">
                {formOwnershipsList.length ? (
                    <>
                        <li>
                            <legend className="ownership-headings">
                                <span>Omistaja</span>
                                <span>Omistajuusprosentti</span>
                            </legend>
                        </li>
                        {formOwnershipsList.map((ownership: IOwnership & {key: string}, index) => (
                            <li
                                className="ownership-item"
                                key={`ownership-item-${ownership.key}`}
                            >
                                <div className="owner">
                                    <FormInputField
                                        inputType="ownership"
                                        label=""
                                        fieldPath="owner.id"
                                        placeholder={
                                            ownership?.owner.name
                                                ? `${ownership?.owner.name} (${ownership?.owner.identifier})`
                                                : ""
                                        }
                                        queryFunction={useGetOwnersQuery}
                                        relatedModelSearchField="name"
                                        getRelatedModelLabel={(obj: IOwner) => formatOwner(obj)}
                                        formData={formOwnershipsList[index]}
                                        setterFunction={handleSetOwnershipLine(index, "owner.id")}
                                        error={error}
                                    />
                                </div>
                                <div className="percentage">
                                    <FormInputField
                                        inputType="number"
                                        label=""
                                        fieldPath="percentage"
                                        fractionDigits={2}
                                        placeholder={ownership.percentage.toString()}
                                        formData={formOwnershipsList[index]}
                                        setterFunction={handleSetOwnershipLine(index, "percentage")}
                                        error={error}
                                    />
                                </div>
                                <div className="icon--remove">
                                    <IconCrossCircle
                                        size="m"
                                        onClick={() => handleRemoveOwnershipLine(index)}
                                    />
                                </div>
                            </li>
                        ))}
                    </>
                ) : (
                    <div style={{textAlign: "center"}}>- Asunnolla ei ole omistajuuksia -</div>
                )}
                {getOwnershipPercentageError(error) && (
                    <>
                        <IconAlertCircleFill className="error-text" />
                        <span className="error-text">{getOwnershipPercentageError(error)}</span>
                    </>
                )}
            </ul>
            <div className="row row--buttons">
                <Button
                    onClick={handleAddOwnershipLine}
                    iconLeft={<IconPlus />}
                    variant="secondary"
                    theme="black"
                >
                    Lisää omistajuus
                </Button>
            </div>
        </>
    );
};

export default OwnershipsList;
