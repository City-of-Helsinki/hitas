import {Button, ButtonPresetTheme, IconDownload} from "hds-react";

const DownloadButton = ({buttonText, ...rest}) => {
    return (
        <Button
            theme={ButtonPresetTheme.Black}
            iconStart={<IconDownload />}
            className="download-button"
            {...rest}
        >
            {buttonText}
        </Button>
    );
};

export default DownloadButton;
