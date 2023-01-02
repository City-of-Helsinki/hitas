import React from "react";

interface HeadingProps {
    children;
    type?: "main" | "list" | "body";
}

const Heading = ({children, type = "main"}: HeadingProps) => {
    switch (type) {
        case "main":
            return <h1 className={`heading--${type}`}>{children}</h1>;
        case "list":
            return <h2 className={`heading--${type}`}>{children}</h2>;
        case "body":
            return <h3 className={`heading--${type}`}>{children}</h3>;
    }
};

export default Heading;
