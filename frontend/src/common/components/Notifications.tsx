import React from "react";

import {keyframes} from "goober";
import {Notification} from "hds-react";
import {useToaster} from "react-hot-toast";

const enterAnimation = `0% {transform: translate3d(0,-200%,0) scale(.6); opacity:.5;} 100% {transform: translate3d(0,0,0) scale(1); opacity:1;}`;
const exitAnimation = `0% {transform: translate3d(0,0,-1px) scale(1); opacity:1;} 100% {transform: translate3d(0,-150%,-1px) scale(.6); opacity:0;}`;
const getAnimationStyle = (visible: boolean): React.CSSProperties => {
    return {
        animation: visible
            ? `${keyframes(enterAnimation)} 0.35s cubic-bezier(.21,1.02,.73,1) forwards`
            : `${keyframes(exitAnimation)} 0.4s forwards cubic-bezier(.06,.71,.55,1)`,
    };
};

export default function Notifications(): JSX.Element {
    const {toasts, handlers} = useToaster();
    const {calculateOffset, updateHeight} = handlers;

    return (
        <>
            {toasts.map((toast) => {
                const offset = calculateOffset(toast, {
                    reverseOrder: false,
                    gutter: 8,
                });

                const ref = (el) => {
                    if (el && typeof toast.height !== "number") {
                        const height = el.getBoundingClientRect().height;
                        updateHeight(toast.id, height);
                    }
                };

                return (
                    <div
                        key={`toast-message-${toast.id}-${toast.createdAt}`}
                        ref={ref}
                        style={{
                            position: "absolute",
                            top: "var(--spacing-layout-s)",
                            right: "var(--spacing-layout-s)",
                            width: "200px",
                            transition: "all 0.3s ease-out",
                            transform: `translateY(${offset}px)`,
                            zIndex: 999,
                        }}
                        {...toast.ariaProps}
                    >
                        <Notification
                            type={(toast.className as "success" | "info" | "error" | "alert") || "success"}
                            closeButtonLabelText={"Sulje"}
                            closeAnimationDuration={1000}
                            boxShadow
                            style={{
                                ...getAnimationStyle(toast.visible),
                                transform: `translateY(${offset}px)`,
                            }}
                            {...toast.ariaProps}
                        >
                            {toast.message as string}
                        </Notification>
                    </div>
                );
            })}
        </>
    );
}
