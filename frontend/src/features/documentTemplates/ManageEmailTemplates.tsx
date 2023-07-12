import {Accordion} from "hds-react";

const ManageEmailTemplates = () => {
    return (
        <div>
            <Accordion heading="Enimmäishintalaskelma" />
            <Accordion heading="Vahvistettu enimmäishintalaskelma" />
            <Accordion heading="Vapautuva yhtiö" />
            <Accordion heading="Valvonnan piiriin jäävä yhtiö" />
        </div>
    );
};

export default ManageEmailTemplates;
