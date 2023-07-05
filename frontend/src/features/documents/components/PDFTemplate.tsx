import {useFieldArray, useForm} from "react-hook-form";
import {useEditPDFTemplateMutation} from "../../../app/services";
import {SaveButton} from "../../../common/components";
import {TextAreaInput} from "../../../common/components/form";
import {hdsToast} from "../../../common/utils";
const instructionTexts = {
    unconfirmed_max_price_calculation: [
        "Teksti velattomasta enimmäishinnasta. Heti asunnon tietoja seuraava kappale. Näytetään lihavoituna.",
        "Teksti lopullisesta enimmäishinnasta, myymisestä ilman enimmäishinnan vahvistamista sekä yhtiölainaosuudesta",
        "Teksti rajahinnan tarkistamisesta. Näytetään lihavoituna.",
    ],
    confirmed_max_price_calculation: [
        "Heti asunnon tietoja seuraava kappale, eli velaton enimmäishinta. Näytetään lihavoituna.",
    ],
    stays_regulated: ["Ohjeteksti"],
    freed_company: ["Ohjeteksti"],
};
const PDFTemplate = ({data, type}) => {
    const [saveTemplate] = useEditPDFTemplateMutation();
    // Get the relevant data from the API response and initialize the form (with field array)
    const currentData = data?.contents.filter((item) => {
        return item.name === type;
    });
    const formObject = useForm({
        defaultValues: {
            paragraphs: currentData[0].texts.map((text) => {
                return {text: text};
            }),
        },
        mode: "all",
    });
    const {control, handleSubmit} = formObject;
    const {fields} = useFieldArray({control, name: "paragraphs"});
    const onSubmit = (submitData) => {
        const data = {
            name: type,
            texts: submitData.paragraphs.map((paragraph) => {
                return paragraph.text;
            }),
        };
        console.log(data);
        saveTemplate({data})
            .unwrap()
            .then(() => hdsToast.success("Päivitys onnistui!"))
            .catch((e) => {
                hdsToast.error("Päivitys epäonnistui!");
                // eslint-disable-next-line no-console
                console.warn(e);
            });
    };
    return (
        <form
            className="current-template"
            onSubmit={handleSubmit(onSubmit)}
        >
            <ul>
                {fields.map((field, index) => (
                    <li key={field.id}>
                        <TextAreaInput
                            name={`paragraphs[${index}].text`}
                            formObject={formObject}
                            label={instructionTexts[data.contents[0].name][index]}
                        />
                    </li>
                ))}
            </ul>
            <div className="row row--buttons">
                <SaveButton
                    type="submit"
                    disabled={false}
                />
            </div>
        </form>
    );
};

export default PDFTemplate;
