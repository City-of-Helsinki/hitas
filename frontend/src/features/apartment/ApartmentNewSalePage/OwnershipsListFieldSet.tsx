import {Button, Fieldset, IconAlertCircleFill, IconCrossCircle, IconPlus} from "hds-react";
import {useFieldArray} from "react-hook-form";
import {v4 as uuidv4} from "uuid";

import {useGetOwnersQuery} from "../../../app/services";
import {NumberInput, RelatedModelInput} from "../../../common/components/form";
import {IOwner, OwnershipsListSchema} from "../../../common/schemas";
import {formatOwner} from "../../../common/utils";

const OwnershipsListFieldSet = ({formObject, disabled}) => {
    const {fields, append, remove} = useFieldArray({
        name: "ownerships",
        control: formObject.control,
        rules: {required: "Kauppatapahtumassa täytyy olla ainakin yksi omistajuus!"},
    });
    formObject.register("ownerships");

    // Blank Ownership. This is appended to the list when user clicks "New ownership"
    const emptyOwnership = {key: uuidv4(), owner: {id: ""} as IOwner, percentage: 100};

    const ownerships = formObject.getValues("ownerships");
    const formErrors = OwnershipsListSchema.safeParse(formObject.getValues("ownerships"));
    const isFormInvalid = !formErrors.success;

    return (
        <Fieldset
            className={`ownerships-fieldset ${isFormInvalid ? "error" : ""}`}
            heading="Omistajuudet *"
        >
            <ul className="ownerships-list">
                {ownerships.length ? (
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
                                        disabled={disabled}
                                    />
                                </div>
                                <div className="percentage">
                                    <NumberInput
                                        name={`ownerships.${index}.percentage`}
                                        fractionDigits={2}
                                        formObject={formObject}
                                        required
                                        disabled={disabled}
                                    />
                                    <span>%</span>
                                </div>
                                <div className={`icon--remove${disabled ? " disabled" : ""}`}>
                                    <IconCrossCircle
                                        size="m"
                                        onClick={() => (disabled ? null : remove(index))}
                                    />
                                </div>
                            </li>
                        ))}
                    </>
                ) : (
                    <div
                        className={isFormInvalid ? "error-text" : ""}
                        style={{textAlign: "center"}}
                    >
                        <IconAlertCircleFill />
                        Asunnolla ei ole omistajuuksia
                        <IconAlertCircleFill />
                    </div>
                )}
            </ul>
            {!formErrors.success && formErrors.error ? (
                <>
                    {formErrors.error.issues.map((e) => (
                        <span key={`${e.code}-${e.message}`}>{e.message}</span>
                    ))}
                </>
            ) : null}
            <div className="row row--buttons">
                <Button
                    iconLeft={<IconPlus />}
                    variant={ownerships.length > 0 ? "secondary" : "primary"}
                    theme="black"
                    onClick={() => append(emptyOwnership)}
                    disabled={disabled}
                >
                    Lisää omistajuus
                </Button>
            </div>
        </Fieldset>
    );
};

export default OwnershipsListFieldSet;
