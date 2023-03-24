export default function Divider({size = "s"}: {size: "s" | "m" | "l"}): JSX.Element {
    return <div className={`divider-horizontal divider-horizontal-${size}`} />;
}
