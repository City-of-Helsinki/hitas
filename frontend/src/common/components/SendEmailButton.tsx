import {Button, IconEnvelope} from "hds-react";

const SendEmailButton = ({...rest}) => (
    <Button
        theme="black"
        iconLeft={<IconEnvelope />}
        {...rest}
    >
        Lähetä sähköposti
    </Button>
);

export default SendEmailButton;
