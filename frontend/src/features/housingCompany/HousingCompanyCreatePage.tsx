import React from "react";

import {Button, IconSaveDisketteFill} from "hds-react";

const HousingCompanyCreatePage = () => {
    return (
        <div className="company-details">
            <h1 className="main-heading">
                <span>Uusi asunto-yhtiö</span>
            </h1>

            <Button iconLeft={<IconSaveDisketteFill />}>Tallenna</Button>
        </div>
    );
};

export default HousingCompanyCreatePage;
