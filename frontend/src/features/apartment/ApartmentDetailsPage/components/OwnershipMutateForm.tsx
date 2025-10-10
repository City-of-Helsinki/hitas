import {zodResolver} from "@hookform/resolvers/zod";
import {Button, ButtonPresetTheme, IconArrowLeft} from "hds-react";
import {useContext, useRef} from "react";
import {useForm} from "react-hook-form";

import {FormProviderForm, NumberInput, SaveFormButton} from "../../../../common/components/forms";
import {IOwnership, IOwnershipUpdate, OwnershipUpdateSchema} from "../../../../common/schemas";
import {useUpdateOwnershipMutation} from "../../../../common/services";
import {hdsToast, setAPIErrorsForFormFields} from "../../../../common/utils";
import {ApartmentViewContext} from "../../components/ApartmentViewContextProvider";

interface OwnershipMutateFormProps {
    defaultObject: IOwnership;
    closeModalAction: () => void;
}

const OwnershipMutateForm = ({defaultObject: ownership, closeModalAction}: OwnershipMutateFormProps) => {
    const {apartment} = useContext(ApartmentViewContext);
    const [updateOwnership, {isLoading}] = useUpdateOwnershipMutation();
    const formRef = useRef<HTMLFormElement>(null);

    const formObject = useForm<IOwnershipUpdate>({
        defaultValues: {percentage: ownership.percentage},
        mode: "all",
        resolver: zodResolver(OwnershipUpdateSchema),
    });

    const {
        formState: {isDirty, isValid},
    } = formObject;

    const onSubmit = (data: IOwnershipUpdate) => {
        if (!isDirty) {
            hdsToast.info("Ei muutoksia omistusosuudessa.");
            closeModalAction();
            return;
        }

        if (!apartment?.id) {
            hdsToast.error("Omistusosuuden tallentaminen epäonnistui.");
            return;
        }

        updateOwnership({
            ownershipId: ownership.id,
            apartmentId: apartment.id,
            data,
        })
            .unwrap()
            .then(() => {
                hdsToast.success("Omistusosuus tallennettu onnistuneesti!");
                closeModalAction();
            })
            .catch((error) => {
                hdsToast.error("Virhe omistusosuuden tallentamisessa!");
                setAPIErrorsForFormFields(formObject, error);
            });
    };

    return (
        <FormProviderForm
            formObject={formObject}
            formRef={formRef}
            onSubmit={onSubmit}
        >
            <NumberInput
                name="percentage"
                label="Omistusosuus"
                unit="%"
                allowDecimals
                required
            />
            <div className="row row--buttons">
                <Button
                    theme={ButtonPresetTheme.Black}
                    iconStart={<IconArrowLeft />}
                    onClick={closeModalAction}
                >
                    Peruuta
                </Button>
                <SaveFormButton
                    formRef={formRef}
                    isLoading={isLoading}
                    disabled={!isValid}
                    buttonText="Tallenna"
                />
            </div>
        </FormProviderForm>
    );
};

export default OwnershipMutateForm;
