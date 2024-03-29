import {useFieldArray, useForm} from "react-hook-form";
import {SaveButton} from "../../../common/components";
import {FormProviderForm, TextAreaInput} from "../../../common/components/forms";
import {useSavePDFTemplateMutation} from "../../../common/services";
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

interface IPDFListResponseData {
    contents: {
        name: string;
        texts: string[];
    }[];
}

const PDFTemplate = ({data, type}: {data: IPDFListResponseData; type: string}) => {
    const [saveTemplate] = useSavePDFTemplateMutation();

    // Get the relevant data from the API response and initialize the form (with field array)
    const currentData =
        data.contents &&
        data.contents.filter((item) => {
            return item.name === type;
        });

    const initialFormParagraphs =
        (currentData &&
            currentData[0]?.texts.map((text) => {
                return {text: text};
            })) ??
        instructionTexts[type].map(() => {
            return {text: ""};
        });

    const formObject = useForm({
        defaultValues: {paragraphs: initialFormParagraphs},
        mode: "all",
    });
    const {control} = formObject;
    const {fields} = useFieldArray({control, name: "paragraphs"});

    const onSubmit = (submitData) => {
        saveTemplate({
            createTemplate: currentData.length === 0,
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
                            label={instructionTexts[type][index]}
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
