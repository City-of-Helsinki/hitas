import {useForm} from "react-hook-form";
import {Select, TextInput} from "./form";
import SendEmailButton from "./SendEmailButton";

type SendEmailFormProps = {
    recipient?: string;
    email: string;
    options: Array<{value: string; label: string}>;
};

const SendEmailForm = ({recipient, email = "", options}: SendEmailFormProps) => {
    const sendEmailForm = useForm({
        defaultValues: {
            email: email,
            template: 0,
        },
        mode: "all",
    });
    const {handleSubmit} = sendEmailForm;
    const sendEmail = (data) => {
        // Validation & implement sending email still missing
        // eslint-disable-next-line no-console
        console.log("Sending email", data);
    };
    return (
        <form
            className="send-email-form"
            onSubmit={handleSubmit(sendEmail)}
        >
            <TextInput
                name="email"
                label={recipient ? recipient + "n sähköpostiosoite" : "Vastaanottajan sähköpostiosoite"}
                formObject={sendEmailForm}
                tooltipText="Käyttää oletuksena relevanttia sähköpostiosoitetta."
                required
            />
            <div className="row row--buttons">
                <Select
                    label="Sähköpostipohja"
                    options={options}
                    defaultValue={options[0]}
                    name="template"
                    formObject={sendEmailForm}
                    required
                />
                <SendEmailButton type="submit" />
            </div>
        </form>
    );
};

export default SendEmailForm;
