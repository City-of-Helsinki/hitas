import {Button, ButtonPresetTheme, Dialog, IconArrowLeft} from "hds-react";
import {TextInput as HDSTextInput, RadioButton} from "hds-react";
import {useRef, useState} from "react";
import {FormProviderForm, RelatedModelInput} from "../forms";
import {useGetOwnersQuery, useMergeOwnersMutation} from "../../services";
import {formatOwner, hdsToast} from "../../utils";
import {useForm} from "react-hook-form";
import {IOwner, IOwnerMergeData} from "../../schemas";
import {SaveButton} from "../index";

export function OwnerMergeForm({firstOwner, cancelAction, closeModal}) {
    const [mergeOwners, {isLoading: isMergeOwnersLoading}] = useMergeOwnersMutation();
    const [isFirstOwnerNameSelected, setIsFirstOwnerNameSelected] = useState(null as boolean | null);
    const [isFirstOwnerIdentifierSelected, setIsFirstOwnerIdentifierSelected] = useState(null as boolean | null);
    const [isFirstOwnerEmailSelected, setIsFirstOwnerEmailSelected] = useState(null as boolean | null);

    const formObject = useForm({
        defaultValues: {
            secondOwner: null as IOwner | null,
        },
        mode: "all",
    });
    const formRef = useRef<HTMLFormElement>(null);
    const secondOwner = formObject.watch("secondOwner");

    const handleSave = () => {
        if (secondOwner === null) {
            hdsToast.error("Valitse yhdistettävä omistaja!");
            return;
        }
        if (isFirstOwnerNameSelected === null) {
            hdsToast.error("Valitse säilytettävä nimi!");
            return;
        }
        if (isFirstOwnerIdentifierSelected === null) {
            hdsToast.error("Valitse säilytettävä henkilö- tai Y-tunnus!");
            return;
        }
        if (isFirstOwnerEmailSelected === null) {
            hdsToast.error("Valitse säilytettävä sähköpostiosoite!");
            return;
        }
        const data: IOwnerMergeData = {
            first_owner_id: firstOwner.id,
            second_owner_id: secondOwner.id,
            should_use_second_owner_name: isFirstOwnerNameSelected === false,
            should_use_second_owner_identifier: isFirstOwnerIdentifierSelected === false,
            should_use_second_owner_email: isFirstOwnerEmailSelected === false,
        };
        mergeOwners({data})
            .unwrap()
            .then((_response) => {
                hdsToast.success("Omistajan tiedot tallennettu onnistuneesti!");
                closeModal();
            })
            .catch((_error) => {
                hdsToast.error("Virhe omistajan tietojen tallentamisessa!");
            });
    };

    return (
        <FormProviderForm
            formObject={formObject}
            formRef={formRef}
            onSubmit={() => {}}
            onSubmitError={() => {}}
        >
            <>
                <div className="row owners-container-row">
                    <div className="column owners-column">
                        <div>
                            <div className="first-owner-heading-label">Valittu omistaja</div>
                            <div className="first-owner-heading">{formatOwner(firstOwner)}</div>
                        </div>
                    </div>
                    <div className="column owners-column">
                        <div>
                            <RelatedModelInput
                                label="Hae yhdistettävä omistaja"
                                required
                                queryFunction={useGetOwnersQuery}
                                relatedModelSearchField="search"
                                name="secondOwner"
                                transform={(obj) => formatOwner(obj)}
                            />
                        </div>
                    </div>
                </div>
                <h2 className="owner-merge-details-heading">Valitse säilytettävät tiedot</h2>
                <div className="row owners-container-row">
                    <div className="column owners-column">
                        <div className="row owner-row">
                            <label
                                className="owner-row-overlay-label"
                                htmlFor="first-owner-radio-name"
                            />
                            <RadioButton
                                id="first-owner-radio-name"
                                name="owner-radio-name"
                                checked={isFirstOwnerNameSelected === true}
                                onChange={() => setIsFirstOwnerNameSelected(true)}
                            />
                            <HDSTextInput
                                id="first-owner-name"
                                name="first-owner-name"
                                label="Nimi"
                                value={firstOwner.name}
                                disabled
                            />
                        </div>
                        <div className="row owner-row">
                            <label
                                className="owner-row-overlay-label"
                                htmlFor="first-owner-radio-identifier"
                            />
                            <RadioButton
                                id="first-owner-radio-identifier"
                                name="owner-radio-identifier"
                                checked={isFirstOwnerIdentifierSelected === true}
                                onChange={() => setIsFirstOwnerIdentifierSelected(true)}
                            />
                            <HDSTextInput
                                id="first-owner-identifier"
                                name="first-owner-identifier"
                                label="Henkilö- tai Y-tunnus"
                                value={firstOwner.identifier}
                                disabled
                            />
                        </div>
                        <div className="row owner-row">
                            <label
                                className="owner-row-overlay-label"
                                htmlFor="first-owner-radio-email"
                            />
                            <RadioButton
                                id="first-owner-radio-email"
                                name="owner-radio-email"
                                checked={isFirstOwnerEmailSelected === true}
                                onChange={() => setIsFirstOwnerEmailSelected(true)}
                            />
                            <HDSTextInput
                                id="first-owner-email"
                                name="first-owner-email"
                                label="Sähköpostiosoite"
                                value={firstOwner.email}
                                disabled
                            />
                        </div>
                    </div>
                    <div className="column owners-column">
                        <div className="row owner-row">
                            <label
                                className="owner-row-overlay-label"
                                htmlFor="second-owner-radio-name"
                            />
                            <HDSTextInput
                                id="second-owner-name"
                                name="second-owner-name"
                                label="Nimi"
                                value={secondOwner?.name ?? ""}
                                disabled
                            />
                            <RadioButton
                                id="second-owner-radio-name"
                                name="owner-radio-name"
                                checked={isFirstOwnerNameSelected === false}
                                onChange={() => setIsFirstOwnerNameSelected(false)}
                            />
                        </div>
                        <div className="row owner-row">
                            <label
                                className="owner-row-overlay-label"
                                htmlFor="second-owner-radio-identifier"
                            />
                            <HDSTextInput
                                id="second-owner-identifier"
                                name="second-owner-identifier"
                                label="Henkilö- tai Y-tunnus"
                                value={secondOwner?.identifier ?? ""}
                                disabled
                            />
                            <RadioButton
                                id="second-owner-radio-identifier"
                                name="owner-radio-identifier"
                                checked={isFirstOwnerIdentifierSelected === false}
                                onChange={() => setIsFirstOwnerIdentifierSelected(false)}
                            />
                        </div>
                        <div className="row owner-row">
                            <label
                                className="owner-row-overlay-label"
                                htmlFor="second-owner-radio-email"
                            />
                            <HDSTextInput
                                id="second-owner-email"
                                name="second-owner-email"
                                label="Sähköpostiosoite"
                                value={secondOwner?.email ?? ""}
                                disabled
                            />
                            <RadioButton
                                id="second-owner-radio-email"
                                name="owner-radio-email"
                                checked={isFirstOwnerEmailSelected === false}
                                onChange={() => setIsFirstOwnerEmailSelected(false)}
                            />
                        </div>
                    </div>
                </div>
                <div className="row row--buttons">
                    <Button
                        theme={ButtonPresetTheme.Black}
                        iconStart={<IconArrowLeft />}
                        onClick={cancelAction}
                    >
                        Peruuta
                    </Button>
                    <SaveButton
                        onClick={handleSave}
                        isLoading={isMergeOwnersLoading}
                        buttonText="Tallenna"
                    />
                </div>
            </>
        </FormProviderForm>
    );
}

export const OwnerMergeModal = ({firstOwner, closeModal, isVisible, setIsVisible}) => {
    return (
        <Dialog
            id="owner-merge-modal"
            aria-labelledby="owner-merge-modal__title"
            className="owner-merge-modal"
            closeButtonLabelText="args.closeButtonLabelText"
            isOpen={isVisible}
            close={closeModal}
            theme={{
                "--accent-line-color": "var(--color-black-80)",
            }}
        >
            <Dialog.Header
                id="owner-merge-modal__title"
                title="Omistajien yhdistäminen"
            />
            <Dialog.Content>
                <OwnerMergeForm
                    firstOwner={firstOwner}
                    cancelAction={() => setIsVisible(false)}
                    closeModal={closeModal}
                />
            </Dialog.Content>
        </Dialog>
    );
};
