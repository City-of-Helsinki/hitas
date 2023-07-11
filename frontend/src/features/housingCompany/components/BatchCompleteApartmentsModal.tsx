import {Button, Dialog} from "hds-react";
import {useState} from "react";
import {useForm} from "react-hook-form";
import {useBatchCompleteApartmentsMutation} from "../../../app/services";
import {CloseButton, SaveDialogModal} from "../../../common/components";
import {DateInput, NumberInput} from "../../../common/components/form";
import {hdsToast, today} from "../../../common/utils";

const BatchCompleteApartmentsModal = ({housingCompanyId}) => {
    const [isFormOpen, setIsFormOpen] = useState(false);
    const [isErrorModalOpen, setIsErrorModalOpen] = useState(false);
    const [batchComplete, {data, error, isLoading}] = useBatchCompleteApartmentsMutation();
    const groupCompleteForm = useForm({
        defaultValues: {
            start: null,
            end: null,
            completion_date: today(),
        },
        mode: "all",
    });
    const {handleSubmit} = groupCompleteForm;
    const formStart = groupCompleteForm.watch("start");
    const formEnd = groupCompleteForm.watch("end");

    const onSubmit = (data: {start: number | null; end: number | null; completion_date: string}) => {
        const submitData = {
            housing_company_id: housingCompanyId,
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
                <form onSubmit={handleSubmit(onSubmit)}>
                    <Dialog.Content>
                        <p>Määritä asunnot, jotka haluat merkitä valmiiksi.</p>
                        <>
                            <p>
                                Jos et halua rajata pelkkää alku- tai loppupäätä jätä kenttä tyhjäksi. Jos kumpikin
                                kenttä on tyhjä valitaan kaikki yhtiön asunnot. Valinta koskee kaikkia rappuja.
                            </p>
                            <div className="apartment-numbers">
                                <div className={formStart ? "toggled" : undefined}>
                                    <NumberInput
                                        name="start"
                                        label="Asuntonumero alku"
                                        formObject={groupCompleteForm}
                                        tooltipText="Jätä kenttä tyhjäksi, jos haluat merkitä valmiiksi kaikki asunnot ennen viimeistä huoneistonumeroa"
                                    />
                                </div>
                                <div className={formEnd ? "toggled" : undefined}>
                                    <NumberInput
                                        name="end"
                                        label="Asuntonumero loppu"
                                        formObject={groupCompleteForm}
                                        tooltipText="Jätä kenttä tyhjäksi, jos haluat merkitä kaikki ensimmäisen valitun jälkeiset asunnot valmiiksi"
                                    />
                                </div>
                            </div>
                            <DateInput
                                name="completion_date"
                                label="Valmistumispäivä"
                                formObject={groupCompleteForm}
                                maxDate={new Date()}
                                defaultValue={new Date()}
                            />
                        </>
                    </Dialog.Content>
                    <Dialog.ActionButtons>
                        <CloseButton onClick={() => setIsFormOpen(false)} />
                        <Button
                            theme="black"
                            type="submit"
                        >
                            Merkitse valmiiksi
                        </Button>
                    </Dialog.ActionButtons>
                </form>
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
