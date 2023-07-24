import {Button, IconDownload} from "hds-react";

const DownloadButton = ({buttonText, ...rest}) => {
    return (
        <Button
            theme="black"
            iconLeft={<IconDownload />}
            className="download-button"
            {...rest}
        >
            {buttonText}
        </Button>
    );
};

export default DownloadButton;
