import {useForm} from "react-hook-form";
import {SaveButton} from "../../../common/components";
import SelectInput from "../../../common/components/form/SelectInput";

const options = [
    {
        label: "00100",
        value: "00100",
    },
    {
        label: "00200",
        value: "00200",
    },
    {
        label: "00300",
        value: "00300",
    },
];

export default function ComparisonSkippedListItem({company}): JSX.Element {
    const formObject = useForm({
        mode: "all",
    });
    const {handleSubmit, watch} = formObject;
    const selectName1 = `${company.id}-1`;
    const selectName2 = `${company.id}-2`;
    const newPostalCode1 = watch(selectName1);
    const newPostalCode2 = watch(selectName2);
    const onSubmit = (data) => {
        console.log(data);
    };
    return (
        <li
            className="results-list__item"
            key={company.id}
        >
            <form onSubmit={handleSubmit(onSubmit)}>
                <span>{company.display_name}</span>
                <div>{company.address.postal_code}</div>
                <SelectInput
                    label="Korvaava postinumero 1"
                    options={options}
                    name={selectName1}
                    formObject={formObject}
                    required
                />
                <SelectInput
                    label="Korvaava postinumero 2"
                    options={options}
                    name={selectName2}
                    formObject={formObject}
                    required
                />
                <SaveButton
                    type="submit"
                    disabled={newPostalCode1 === undefined || newPostalCode2 === undefined}
                />
            </form>
        </li>
    );
}
