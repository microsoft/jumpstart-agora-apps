import React from "react";

interface ReportCardProps {
    className?: string;
    title: string;
    value?: string | number;
    unit?: string;
    standardValue?: string | number;
    expressValue?: string | number;
    selfServiceValue?: string | number;
}

function ReportCard(props: ReportCardProps) {
    return (
        <div className={"bg-secondary rounded p-3 " + props.className}>
            <div className="row pb-4">
                <div className="col text-white h6 mb-1">{props.title}</div>
                <div className="col text-white display-6 fw-bold text-end">{props.value ?? 0}</div>
            </div>
            <div className="d-flex justify-content-between align-items-center px-3 py-1 mb-2 border border-purple border-1 bg-secondary-light rounded">
                <div className="text-white fs-6">Standard</div>
                <div className="text-white fs-5 fw-bold">
                    {props.standardValue ?? 0}
                    {props.unit && <span className="fs-7 fw-normal ms-1">{props.unit}</span>}
                </div>
            </div>
            <div className="d-flex justify-content-between align-items-center px-3 py-1 mb-2 border border-yellow border-1 bg-secondary-light rounded">
                <div className="text-white fs-6">Express</div>
                <div className="text-white fs-5 fw-bold">
                    {props.expressValue ?? 0}
                    {props.unit && <span className="fs-7 fw-normal ms-1">{props.unit}</span>}
                </div>
            </div>
            <div className="d-flex justify-content-between align-items-center px-3 py-1 border border-cyan border-1 bg-secondary-light rounded">
                <div className="text-white fs-6">Self Service</div>
                <div className="text-white fs-5 fw-bold">
                    {props.selfServiceValue ?? 0}
                    {props.unit && <span className="fs-7 fw-normal ms-1">{props.unit}</span>}
                </div>
            </div>
        </div>
    );
}

export default ReportCard;
