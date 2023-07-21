import {useFieldArray, useForm} from "react-hook-form";
import {SaveButton} from "../../../common/components";
import {FormProviderForm, TextAreaInput} from "../../../common/components/forms";
import {useEditPDFTemplateMutation} from "../../../common/services";
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
    stays_regulated: ["Hintasääntelystä vapautuminen", "Tontin maanvuokra", "Hintasääntelyn jatkuminen"],
    released_from_regulation: ["Hintasääntelystä vapautuminen"],
};

const PDFTemplate = ({data, type}) => {
    const [saveTemplate] = useEditPDFTemplateMutation();
    // Get the relevant data from the API response and initialize the form (with field array)
    const currentData = data?.contents.filter((item) => {
        return item.name === type;
    });
    const formObject = useForm({
        defaultValues: {
            paragraphs: currentData[0]?.texts.map((text) => {
                return {text: text};
            }),
        },
        mode: "all",
    });
    const {control} = formObject;
    const {fields} = useFieldArray({control, name: "paragraphs"});

    const onSubmit = (submitData) => {
        saveTemplate({
            name: type,
            texts: submitData.paragraphs.map((paragraph) => paragraph.text),
        })
            .unwrap()
            .then(() => hdsToast.success("Päivitys onnistui!"))
            .catch((e) => {
                hdsToast.error("Päivitys epäonnistui!");
                // eslint-disable-next-line no-console
                console.warn(e);
            });
    };

    return (
        <FormProviderForm
            formObject={formObject}
            className="current-template"
            onSubmit={onSubmit}
        >
            <ul>
                {fields.map((field, index) => (
                    <li key={field.id}>
                        <TextAreaInput
                            name={`paragraphs[${index}].text`}
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
        </FormProviderForm>
    );
};

export default PDFTemplate;
