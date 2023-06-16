import {Button, Dialog} from "hds-react";
import {useState} from "react";
import {useForm} from "react-hook-form";
import {useBatchCompleteApartmentsMutation} from "../../app/services";
import {CloseButton} from "../../common/components";
import {NumberInput} from "../../common/components/form";
import {hdsToast, today} from "../../common/utils";

const BatchCompleteApartmentsModal = ({housingCompanyId}) => {
    const [isOpen, setIsOpen] = useState(false);
    const [batchComplete] = useBatchCompleteApartmentsMutation();
    const groupCompleteForm = useForm({
        defaultValues: {
            start: 1,
            end: null,
        },
        mode: "all",
    });
    const {handleSubmit, setFocus} = groupCompleteForm;
    const onSubmit = (data: {start: number | null; end: number | null}) => {
        const submitData = {
            housing_company_id: housingCompanyId,
            data: {
                apartment_number_start: data.start as number,
                apartment_number_end: data.end as number,
                completion_date: today(),
            },
        };
        console.log("To API:", submitData);
        batchComplete({data: submitData})
            .then((data) => {
                console.log("API response:", data);
                hdsToast.success("Asunnot merkitty valmiiksi");
            })
            .catch((e) => {
                // eslint-disable-next-line no-console
                console.warn(e);
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
                    setIsOpen(true);
                    setFocus("end"); // FIXME: This doesn't work :/
                }}
            >
                Merkitse valmiiksi
            </Button>
            <Dialog
                id="batch-complete-modal"
                aria-labelledby="batch-complete-modal"
                isOpen={isOpen}
            >
                <Dialog.Header
                    title="Merkitse sarja valmiiksi"
                    id="batch-complete-modal__header"
                />
                <form onSubmit={handleSubmit(onSubmit)}>
                    <Dialog.Content>
                        <div className="apartment-numbers">
                            <NumberInput
                                name="start"
                                label="Asunnosta"
                                formObject={groupCompleteForm}
                                required
                            />
                            <NumberInput
                                name="end"
                                label="Asuntoon"
                                formObject={groupCompleteForm}
                                required
                            />
                        </div>
                    </Dialog.Content>
                    <Dialog.ActionButtons>
                        <CloseButton onClick={() => setIsOpen(false)} />
                        <Button
                            theme="black"
                            type="submit"
                            disabled={groupCompleteForm.getValues("end") === null}
                        >
                            Merkitse valmiiksi
                        </Button>
                    </Dialog.ActionButtons>
                </form>
            </Dialog>
        </>
    );
};

export default BatchCompleteApartmentsModal;
