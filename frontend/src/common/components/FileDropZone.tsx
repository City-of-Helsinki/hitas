import React, {useEffect} from "react";

interface FileDropZoneProps {
    onDraggingChange?: (isDragging: boolean) => void;
    onFileDrop: (files: FileList) => void;
    helpText?: string;
}

export default function FileDropZone({
    onDraggingChange = () => {},
    onFileDrop,
    helpText,
}: FileDropZoneProps): React.JSX.Element {
    useEffect(() => {
        let isDragging = document.documentElement.classList.contains("is-dragging");
        let dragEndTimeout;

        const startDrag = () => {
            if (!isDragging) {
                isDragging = true;
                document.documentElement.classList.add("is-dragging");
                onDraggingChange(true);
                // Failsafe in case the dragleave is somehow missed and the user is no longer dragging
                window.addEventListener("mousemove", handleMouseMove);
            }
        };

        const endDrag = () => {
            if (isDragging) {
                isDragging = false;
                document.documentElement.classList.remove("is-dragging");
                onDraggingChange(false);
                document
                    .querySelector(".file-drop-zone.is-dragging-over-drop-zone")
                    ?.classList.remove("is-dragging-over-drop-zone");
                window.removeEventListener("mousemove", handleMouseMove);
            }
        };

        const handleDragEnter = (event) => {
            event.preventDefault();
            dragEndTimeout = clearTimeout(dragEndTimeout);
            startDrag();
            if (event.target.classList.contains("file-drop-zone")) {
                event.target.classList.add("is-dragging-over-drop-zone");
            }
        };

        const handleDragOver = (event) => {
            event.preventDefault();
            dragEndTimeout = clearTimeout(dragEndTimeout);
        };

        const handleDragLeave = (event) => {
            event.preventDefault();
            dragEndTimeout = setTimeout(endDrag, 200);
            if (event.target.classList.contains("file-drop-zone")) {
                event.target.classList.remove("is-dragging-over-drop-zone");
            }
        };

        const handleDrop = (event) => {
            event.preventDefault();
            endDrag();
            if (
                event.target.classList.contains("file-drop-zone") &&
                event.dataTransfer.files &&
                event.dataTransfer.files.length > 0
            ) {
                onFileDrop(event.dataTransfer.files);
            }
        };

        const handleMouseMove = (event) => {
            // Failsafe in case the dragleave is somehow missed and the user is no longer dragging
            if (event.buttons === 0) {
                endDrag();
            }
        };

        window.addEventListener("dragenter", handleDragEnter);
        window.addEventListener("dragover", handleDragOver);
        window.addEventListener("dragleave", handleDragLeave);
        window.addEventListener("drop", handleDrop);

        return () => {
            window.removeEventListener("dragenter", handleDragEnter);
            window.removeEventListener("dragover", handleDragOver);
            window.removeEventListener("dragleave", handleDragLeave);
            window.removeEventListener("drop", handleDrop);
            window.removeEventListener("mousemove", handleMouseMove);
        };
    }, [onDraggingChange]);

    return (
        <>
            <div className="file-drop-zone">
                <div className="file-drop-zone-helptext">{helpText ?? "Pudota tiedostot tähän."}</div>
            </div>
        </>
    );
}
