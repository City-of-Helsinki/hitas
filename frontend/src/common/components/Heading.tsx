interface HeadingProps {
    children;
    className?: string;
    type?: "main" | "list" | "body";
}

const Heading = ({children, className, type = "main"}: HeadingProps) => {
    switch (type) {
        case "main":
            return <h1 className={`heading--${type} ${className}`}>{children}</h1>;
        case "list":
            return <h2 className={`heading--${type} ${className}`}>{children}</h2>;
        case "body":
            return <h3 className={`heading--${type} ${className}`}>{children}</h3>;
    }
};

export default Heading;
