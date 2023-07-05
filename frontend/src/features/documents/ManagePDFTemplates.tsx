import {Tab, TabList, TabPanel, Tabs} from "hds-react";
import {useFieldArray, useForm} from "react-hook-form";
import {TextAreaInput} from "../../common/components/form";

const paragraphArray = [
    {
        text: "Hitas-huoneistonne velaton enimmäishinta on 272 700 euroa. Velaton enimmäishinta on laskettu voimassaolevan rajahinnan perusteella (60.00 m² * 4545.00 euroa).",
    },
    {
        text: "Mikäli tarvitsette huoneistonne vahvistetun enimmäishinnan, teidän tulee toimittaa isännöitsijäntodistus tai Hitas-enimmäishinnan vahvistamislomake. Näiden tietojen perusteella vahvistetaan huoneistonne lopullinen enimmäishinta. Laskelma tulee huoneistoa myytäessä esittää ostajille.",
    },
    {
        text: "Teillä on mahdollisuus myydä huoneistonne myös ilman enimmäishinnan vahvistamista enintään kaupantekoajankohtana voimassaolevalla rajahinnalla. Rajahinnan alittavasta velattomasta huoneiston hinnasta voidaan myyjän ja ostajan välillä sopia vapaasti.",
    },
    {
        text: "Mikäli osakkeisiin kohdistuu yhtiölainaosuutta, tulee sen osuus vähentää huoneiston velattomasta hinnasta kauppahintaa laskettaessa.",
    },
    {
        text: "Rajahintaa tarkistetaan neljännesvuosittain 1.2., 1.5., 1.8. ja 1.11. ja se on voimassa kolme kuukautta kerrallaan.",
    },
];

const CurrentTemplate = () => {
    const formObject = useForm({
        defaultValues: {
            paragraphs: paragraphArray,
        },
        mode: "all",
    });
    const {control} = formObject;
    const {fields} = useFieldArray({control, name: "paragraphs"});
    return (
        <div className="current-template">
            <ul>
                {fields.map((field, index) => (
                    <li key={field.id}>
                        <TextAreaInput
                            name={`paragraphs[${index}].text`}
                            formObject={formObject}
                            label={`Kappale ${index + 1}`}
                        />
                        <div className="instruction-text">Ohjeteksti</div>
                    </li>
                ))}
            </ul>
            <div className="example-result">
                {fields.map((field) => (
                    <p key={field.id}>{field.text}</p>
                ))}
            </div>
        </div>
    );
};

const ManagePDFTemplates = () => {
    return (
        <div>
            <Tabs>
                <TabList>
                    <Tab>Vapautuva yhtiö</Tab>
                    <Tab>Valvonnan piiriin jäävä yhtiö</Tab>
                    <Tab>Enimmäishintalaskelma</Tab>
                    <Tab>Hinta-arvio</Tab>
                </TabList>
                <TabPanel>
                    <h2>Vapautuva yhtiö</h2>
                    <CurrentTemplate />
                </TabPanel>
                <TabPanel>
                    <h2>Valvonnan piiriin jäävä yhtiö</h2>
                </TabPanel>
                <TabPanel>
                    <h2>Enimmäishintalaskelma</h2>
                </TabPanel>
                <TabPanel>
                    <h2>Hinta-arvio</h2>
                </TabPanel>
            </Tabs>
        </div>
    );
};

export default ManagePDFTemplates;
