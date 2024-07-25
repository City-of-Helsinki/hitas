import {Button, IconCrossCircle, IconPlus} from "hds-react";
import {useFieldArray, useFormContext} from "react-hook-form";
import {v4 as uuidv4} from "uuid";
import {OwnershipsListSchema} from "../schemas";
import {useGetOwnersQuery} from "../services";
import {formatOwner} from "../utils";
import {SimpleErrorMessage} from "./";
import {NumberInput, RelatedModelInput} from "./forms";
import {OwnerMutateForm} from "./mutateComponents";

const OwnershipList = () => {
    const formObject = useFormContext();

    const {fields, append, remove} = useFieldArray({
        name: "ownerships",
        control: formObject.control,
        rules: {required: "Kauppatapahtumassa täytyy olla ainakin yksi omistajuus!"},
    });
    formObject.register("ownerships");

    // Blank Ownership. This is appended to the list when user clicks "New ownership"
    const emptyOwnership = {key: uuidv4(), owner: undefined, percentage: 100};

    const formErrors = OwnershipsListSchema.safeParse(formObject.getValues("ownerships"));

    return (
        <>
            <ul className="ownerships-list">
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
                                    relatedModelSearchField="search"
                                    name={`ownerships.${index}.owner`}
                                    transform={(obj) => formatOwner(obj)}
                                    RelatedModelMutateComponent={OwnerMutateForm}
                                    isModalDefaultOpen={formObject.getValues(`ownerships.${index}.owner`) === undefined}
                                />
                            </div>
                            <div className="percentage">
                                <NumberInput
                                    name={`ownerships.${index}.percentage`}
                                    allowDecimals
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
            </ul>

            <>
                {!formErrors.success &&
                    formErrors.error &&
                    formErrors.error.issues.map((e, index) => (
                        <SimpleErrorMessage
                            key={`${index}-${e.code}-${e.message}`}
                            errorMessage={e.message}
                        />
                    ))}
            </>

            <div className="row row--buttons">
                <Button
                    iconLeft={<IconPlus />}
                    variant={formObject.watch("ownerships").length > 0 ? "secondary" : "primary"}
                    theme="black"
                    onClick={() => append(emptyOwnership)}
                >
                    Lisää uusi omistajuusrivi
                </Button>
            </div>
        </>
    );
};

export default OwnershipList;
