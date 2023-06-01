import {IconAlertCircleFill} from "hds-react";

export default function SimpleErrorMessage({errorMessage}: {errorMessage?: string}) {
    if (errorMessage) {
        return (
            <p className="error-text">
                <IconAlertCircleFill />
                {errorMessage}
            </p>
        );
    }
    return null;
}
