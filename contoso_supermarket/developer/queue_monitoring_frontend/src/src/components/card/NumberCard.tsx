import React from "react";

interface NumberCardProps {
    value?: string | number;
    title: string;
    subTitle?: string;
    className?: string;
}

function NumberCard(props: NumberCardProps) {
    return (
        <div className={" bg-secondary p-3 ratio ratio-1x1 d-flex flex-column" + (props.className ? ` ${props.className}` : "")}>
            <div className="text-white fs-1 justify-content-center  d-flex flex-column align-items-center relative place-content-center">
                <div className="inline-block flex-1">{props.value}</div>
                <div className="text-white text-xs text-center h-0">{props.subTitle}</div>
                <div className="text-primary fs-5 text-center">{props.title}</div>
            </div>
        </div>
    );
}

export default NumberCard;
