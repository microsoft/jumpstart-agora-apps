import dayjs from "dayjs";
import React from "react";

interface ReportCardProps {
    className?: string;
    title: string;
    value?: number;
    unit?: string;
    standardThresholdValue?: number;
    expressThresholdValue?: number;
    selfServiceThresholdValue?: number;
    standardValue?: number;
    expressValue?: number;
    selfServiceValue?: number;
    standardClosed: boolean;
    expressClosed: boolean;
    selfServiceClosed: boolean;
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
    const standardValue = props.standardValue ?? 0;
    const expressValue = props.expressValue ?? 0;
    const selfServiceValue = props.selfServiceValue ?? 0;

    const standardThresholdValue = props.standardThresholdValue ?? 0;
    const expressThresholdValue = props.expressThresholdValue ?? 0;
    const selfServiceThresholdValue = props.selfServiceThresholdValue ?? 0;

    const getBackgroundClass = (closed: boolean, value: number) => {
        if (closed) {
            return "bg-secondary-light text-white";
        } else if (value <= 2) {
            return "bg-success";
        } else if (value <= 4) {
            return "bg-warning";
        } else {
            return "bg-danger text-white";
        }
    };
    return (
        <div className={"bg-secondary rounded p-3 " + props.className}>
            <div className="row pb-5">
                <div className="col text-white h6 mb-1">{props.title}</div>
                <div className="col text-white display-6 fw-bold text-end">{formatNumber(props.value ?? 0)}</div>
            </div>
            <div
                className={
                    "d-flex justify-content-between align-items-center px-3 py-1 mb-2 rounded " +
                    getBackgroundClass(props.standardClosed, standardThresholdValue)
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
                    "d-flex justify-content-between align-items-center px-3 py-1 mb-2 rounded " +
                    getBackgroundClass(props.expressClosed, expressThresholdValue)
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
                    "d-flex justify-content-between align-items-center px-3 py-1 mb-2 rounded " +
                    getBackgroundClass(props.selfServiceClosed, selfServiceThresholdValue)
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
