import {Button, IconAlertCircleFill, IconCrossCircle, IconPlus} from "hds-react";
import {useFieldArray} from "react-hook-form";
import {v4 as uuidv4} from "uuid";

import {useGetOwnersQuery} from "../../../app/services";
import {NumberInput, RelatedModelInput} from "../../../common/components/form";
import {IOwner, IOwnership} from "../../../common/schemas";
import {formatOwner} from "../../../common/utils";

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

    // Ownerships
    const emptyOwnership = {key: uuidv4(), owner: {id: ""} as IOwner, percentage: 0};

    formObject.register("ownerships");

    return (
        <div>
            <ul className="ownerships-list">
                {formOwnershipsList.length ? (
                    <>
                        <li>
                            <legend className="ownership-headings">
                                <span>Omistaja *</span>
                                <span>Osuus *</span>
                            </legend>
                        </li>
                        {fields.map((field, index) => (
                            <li
                                className="ownership-item"
                                key={field.id}
                            >
                                <div className="owner">
                                    <RelatedModelInput
                                        label="Omistaja"
                                        required
                                        queryFunction={useGetOwnersQuery}
                                        relatedModelSearchField="name"
                                        formObject={formObject}
                                        formObjectFieldPath={`ownerships.${index}.owner`}
                                        formatFormObjectValue={(obj) => (obj.id ? formatOwner(obj) : "")}
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
