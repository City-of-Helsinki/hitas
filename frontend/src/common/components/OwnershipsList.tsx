import {Button, IconAlertCircleFill, IconCrossCircle, IconPlus} from "hds-react";
import {Control, useFieldArray, useWatch} from "react-hook-form";
import {v4 as uuidv4} from "uuid";

import {useGetOwnersQuery} from "../../app/services";
import {IOwner, IOwnership} from "../schemas";
import {formatOwner} from "../utils";
import {NumberInput, RelatedModelInput} from "./form";

type FormValues = {
    ownerships: IOwnership[];
};

const OwnershipsList = ({
    formOwnershipsList,
    noOwnersError = false,
    formObject,
}: {
    formOwnershipsList: IOwnership[];
    noOwnersError?: boolean;
    formObject?;
}) => {
    const {fields, append, remove} = useFieldArray({
        name: "ownerships",
        control: formObject.control,
        rules: {required: "Kauppatapahtumassa täytyy olla ainakin yksi omistajuus!"},
    });
    const getTotal = (payload) => {
        let sum = 0;
        for (const item of payload) {
            sum = sum + (Number.isNaN(item.percentage) ? 0 : item.percentage);
        }
        return sum;
    };

    // Ownerships
    const emptyOwnership = {key: uuidv4(), owner: {id: ""} as IOwner, percentage: 0};

    function TotalAmount({control}: {control: Control<FormValues>}) {
        const ownershipValues = useWatch({control, name: "ownerships"});
        return <span>{getTotal(ownershipValues)}</span>;
    }

    return (
        <div>
            <ul className="ownerships-list">
                {formOwnershipsList.length ? (
                    <>
                        <li>
                            <legend className="ownership-headings">
                                <span>Omistaja *</span>
                                <span>
                                    Omistajuusprosentti (<TotalAmount control={formObject.control} /> / 100%) *
                                </span>
                            </legend>
                        </li>
                        {fields.map((field, index) => (
                            <li
                                className="ownership-item"
                                key={field.id}
                            >
                                <div className="owner">
                                    <RelatedModelInput
                                        name={`ownerships.${index}.owner.id`}
                                        fieldPath="owner.id"
                                        queryFunction={useGetOwnersQuery}
                                        relatedModelSearchField="name"
                                        getRelatedModelLabel={(obj) => formatOwner(obj)}
                                        formObject={formObject}
                                        placeholder={
                                            formObject.getValues(`ownerships.${index}.owner.name`)
                                                ? `${formObject.getValues(
                                                      `ownerships.${index}.owner.name`
                                                  )} (${formObject.getValues(`ownerships.${index}.owner.identifier`)})`
                                                : ""
                                        }
                                        required
                                    />
                                </div>
                                <div className="percentage">
                                    <NumberInput
                                        name={`ownerships.${index}.percentage`}
                                        fractionDigits={2}
                                        formObject={formObject}
                                        required
                                    />
                                    <span>%</span>
                                </div>
                                <div className="icon--remove">
                                    <IconCrossCircle
                                        size="m"
                                        onClick={() => remove(index)}
                                    />
                                </div>
                            </li>
                        ))}
                    </>
                ) : (
                    <div
                        className={noOwnersError ? "error-text" : ""}
                        style={{textAlign: "center"}}
                    >
                        <IconAlertCircleFill />
                        Asunnolla ei ole omistajuuksia
                        <IconAlertCircleFill />
                    </div>
                )}
            </ul>
            <div className="row row--buttons">
                <Button
                    iconLeft={<IconPlus />}
                    variant={formOwnershipsList.length > 0 ? "secondary" : "primary"}
                    theme="black"
                    onClick={() => append(emptyOwnership)}
                >
                    Lisää omistajuus
                </Button>
            </div>
        </div>
    );
};

export default OwnershipsList;
