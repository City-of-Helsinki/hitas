import {Button, IconDownload} from "hds-react";

const DownloadButton = ({downloadFn, buttonText, ...buttonProps}) => {
    return (
        <Button
            onClick={downloadFn}
            theme="black"
            iconLeft={<IconDownload />}
            {...buttonProps}
        >
            {buttonText}
        </Button>
    );
};

export default DownloadButton;
