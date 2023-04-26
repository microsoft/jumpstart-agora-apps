import React from "react";
import { Modal } from "react-bootstrap";

interface ModalProps {
    onCancelButtonClick: () => void;
    onActionButtonClick: () => void;
    title: string;
    body: string;
    actionButtonText: string;
    actionButtonClass?: string;
    cancelButtonText: string;
    open: boolean;
    setOpen: (open: boolean) => void;
}

function ModalConfirmation(props: ModalProps) {
    return (
        <Modal show={props.open} onHide={() => props.setOpen(false)}>
            <Modal.Header className="border-0" closeButton>
                <Modal.Title className="text-primary">{props.title}</Modal.Title>
            </Modal.Header>
            <Modal.Body>{props.body}</Modal.Body>
            <Modal.Footer className="border-0">
                <button
                    className="btn px-5 ms-auto"
                    onClick={() => {
                        props.onCancelButtonClick();
                        props.setOpen(false);
                    }}
                >
                    {props.cancelButtonText}
                </button>
                <button
                    className={"btn text-white px-5 " + props.actionButtonClass}
                    onClick={() => {
                        props.onActionButtonClick();
                        props.setOpen(false);
                    }}
                >
                    {props.actionButtonText}
                </button>
            </Modal.Footer>
        </Modal>
    );
}

export default ModalConfirmation;
