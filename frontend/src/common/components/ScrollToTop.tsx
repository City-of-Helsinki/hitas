import {useEffect} from "react";

import {useLocation} from "react-router-dom";

export default function ScrollToTop() {
    // Scroll user to the top of the page when they change pages
    // refs. https://stackoverflow.com/a/71753162/12730861
    const {pathname} = useLocation();

    useEffect(() => {
        const isScrollRestorationControllable = "scrollRestoration" in window.history;
        if (isScrollRestorationControllable) {
            window.history.scrollRestoration = "manual";
        }

        // This does nothing: `window.scrollTo(0, 0)`
        // because the main scroll container is the App div.
        document.querySelector(".App")?.scrollTo(0, 0);
    }, [pathname]);

    return <></>;
}
