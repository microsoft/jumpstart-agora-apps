import dayjs from "dayjs";
import React from "react";

interface ReportCardProps {
    className?: string;
    title: string;
    value?: number;
    unit?: string;
    standardValue?: number;
    standardThreshold: number;
    expressValue?: number;
    expressThreshold: number;
    selfServiceValue?: number;
    selfServiceThreshold: number;
}

//format number to x decimal points
const formatNumber = (num: number, minDigits?: number, maxDigits?: number) => {
    if (isNaN(num)) {
        return 0;
    }
    return num.toLocaleString(dayjs.locale(), {
        minimumFractionDigits: minDigits ?? 0,
        maximumFractionDigits: maxDigits ?? 1,
    });
};

function ReportCard(props: ReportCardProps) {
    const standardThreshold = props.standardThreshold ?? 0;
    const expressThreshold = props.expressThreshold ?? 0;
    const selfServiceThreshold = props.selfServiceThreshold ?? 0;
    const standardValue = props.standardValue ?? 0;
    const expressValue = props.expressValue ?? 0;
    const selfServiceValue = props.selfServiceValue ?? 0;

    return (
        <div className={"bg-secondary rounded p-3 " + props.className}>
            <div className="row pb-5">
                <div className="col text-white h6 mb-1">{props.title}</div>
                <div className="col text-white display-6 fw-bold text-end">{formatNumber(props.value ?? 0)}</div>
            </div>
            <div
                className={
                    "d-flex justify-content-between align-items-center px-3 py-1 mb-2 bg-secondary-light rounded " +
                    (standardValue >= standardThreshold ? "bg-danger text-white" : "bg-success text-black")
                }
            >
                <div className="fs-6 fw-semibold">Standard</div>
                <div className="fs-5 fw-bold">
                    {formatNumber(standardValue)}
                    {props.unit && <span className="fs-7 fw-normal ms-1">{props.unit}</span>}
                </div>
            </div>
            <div
                className={
                    "d-flex justify-content-between align-items-center px-3 py-1 mb-2 bg-secondary-light rounded " +
                    (expressValue >= expressThreshold ? "bg-danger text-white" : "bg-success text-black")
                }
            >
                <div className="fs-6 fw-semibold">Express</div>
                <div className="fs-5 fw-bold">
                    {formatNumber(expressValue)}
                    {props.unit && <span className="fs-7 fw-normal ms-1">{props.unit}</span>}
                </div>
            </div>
            <div
                className={
                    "d-flex justify-content-between align-items-center px-3 py-1 mb-2 bg-secondary-light rounded " +
                    (selfServiceValue >= selfServiceThreshold ? "bg-danger text-white" : "bg-success text-black")
                }
            >
                <div className="fs-6 fw-semibold">Self Service</div>
                <div className="fs-5 fw-bold">
                    {formatNumber(selfServiceValue)}
                    {props.unit && <span className="fs-7 fw-normal ms-1">{props.unit}</span>}
                </div>
            </div>
        </div>
    );
}

export default ReportCard;
