import {Button, Dialog} from "hds-react";
import {useRef, useState} from "react";
import {useForm} from "react-hook-form";
import {CloseButton, SaveDialogModal} from "../../../common/components";
import {DateInput, FormProviderForm, NumberInput} from "../../../common/components/forms";
import {useBatchCompleteApartmentsMutation} from "../../../common/services";
import {hdsToast, today} from "../../../common/utils";

const BatchCompleteApartmentsModal = ({housingCompany}) => {
    const [isFormOpen, setIsFormOpen] = useState(false);
    const [isErrorModalOpen, setIsErrorModalOpen] = useState(false);
    const [batchComplete, {data, error, isLoading}] = useBatchCompleteApartmentsMutation();

    const formRef = useRef<HTMLFormElement>(null);
    const formObject = useForm({
        defaultValues: {
            start: null,
            end: null,
            completion_date: today(),
        },
        mode: "all",
    });

    const handleConfirmButtonClick = () => {
        formRef.current && formRef.current.dispatchEvent(new Event("submit", {cancelable: true, bubbles: true}));
    };

    const onSubmit = (data: {start: number | null; end: number | null; completion_date: string}) => {
        const submitData = {
            housing_company_id: housingCompany.id,
            data: {
                apartment_number_start: data.start !== undefined && data.start !== null ? Number(data.start) : null,
                apartment_number_end: data.end !== undefined && data.end !== null ? Number(data.end) : null,
                completion_date: data.completion_date,
            },
        };
        batchComplete(submitData)
            .then((data) => {
                hdsToast.success(
                    (data as {data: {completed_apartment_count: number}}).data.completed_apartment_count +
                        " asuntoa merkitty onnistuneesti valmiiksi"
                );
                setIsFormOpen(false);
            })
            .catch((e) => {
                // eslint-disable-next-line no-console
                console.warn(e);
                setIsErrorModalOpen(true);
                hdsToast.error("Asuntojen merkitseminen valmiiksi epäonnistui");
            });
    };

    return (
        <>
            <Button
                theme="black"
                size="small"
                variant="secondary"
                onClick={() => {
                    setIsFormOpen(true);
                }}
                disabled={isLoading || housingCompany.regulation_status !== "regulated"}
            >
                Merkitse valmiiksi
            </Button>
            <Dialog
                id="batch-complete-modal"
                aria-labelledby="batch-complete-modal"
                isOpen={isFormOpen}
            >
                <Dialog.Header
                    title="Merkitse asunnot valmiiksi"
                    id="batch-complete-modal__header"
                />
                <Dialog.Content>
                    <FormProviderForm
                        formObject={formObject}
                        formRef={formRef}
                        onSubmit={onSubmit}
                    >
                        <p>Määritä asunnot, jotka haluat merkitä valmiiksi.</p>
                        <p>
                            Rajaa asuntojen valmiiksi merkitsemistä asunnon numeron perusteella. Voit myös jättää kentän
                            tyhjäksi, mikäli et halua rajata asuntoja alku- tai loppunumeron perusteella. Jos molemmat
                            kentät jätetään tyhjäksi, kaikki yhtiön asunnot valitaan valmiiksi merkittäväksi. Asuntoja
                            ei rajata asunnon rapun perusteella.
                        </p>
                        <div className="apartment-numbers">
                            <div className={formObject.watch("start") ? "toggled" : undefined}>
                                <NumberInput
                                    name="start"
                                    label="Ensimmäinen asuntonumero"
                                    tooltipText="Rajaa pienimmän asunnon numeron joka valitaan valmiiksi merkittäväksi.
                                        Mikäli kenttä jätetään tyhjäksi valitaan kaikki asunnot, joiden asuntonumero on pienempi tai yhtäsuuri kuin viimeinen valittu asuntonumero."
                                />
                            </div>
                            <div className={formObject.watch("end") ? "toggled" : undefined}>
                                <NumberInput
                                    name="end"
                                    label="Viimeinen asuntonumero"
                                    tooltipText="Rajaa suurimman asunnon numeron joka valitaan valmiiksi merkittäväksi.
                                        Mikäli kenttä jätetään tyhjäksi valitaan kaikki asunnot, joiden asuntonumero on yhtäsuuri tai suurempi kuin ensimmäinen valittu asuntonumero."
                                />
                            </div>
                        </div>
                        <DateInput
                            name="completion_date"
                            label="Valmistumispäivä"
                            maxDate={new Date()}
                            defaultValue={new Date()}
                        />
                    </FormProviderForm>
                </Dialog.Content>
                <Dialog.ActionButtons>
                    <CloseButton onClick={() => setIsFormOpen(false)} />
                    <Button
                        theme="black"
                        onClick={() => handleConfirmButtonClick()}
                    >
                        Merkitse valmiiksi
                    </Button>
                </Dialog.ActionButtons>
            </Dialog>
            <SaveDialogModal
                data={data}
                error={error}
                isLoading={isLoading}
                isVisible={isErrorModalOpen}
                setIsVisible={setIsErrorModalOpen}
                className="batch-complete-error-modal"
            />
        </>
    );
};

export default BatchCompleteApartmentsModal;
