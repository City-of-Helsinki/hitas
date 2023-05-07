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
        mode: "onChange",
    });
    const {handleSubmit, watch} = formObject;
    const newPostalCode = watch(company.id);
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
                    label="Korvaava postinumero"
                    options={options}
                    name={company.id}
                    formObject={formObject}
                    required
                />
                <SaveButton
                    type="submit"
                    disabled={newPostalCode === undefined}
                />
            </form>
        </li>
    );
}
