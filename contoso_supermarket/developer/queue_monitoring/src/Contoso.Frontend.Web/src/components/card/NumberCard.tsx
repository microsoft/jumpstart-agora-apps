import React from 'react';

interface NumberCardProps {
    value?: string | number;
    title: string;
    subTitle?: string;
    className?: string;
}

function NumberCard(props: NumberCardProps) {
    return (
        <div className={"flex flex-col " + props.className}>
            <div className="text-white text-5xl self-center flex-1 flex flex-col items-center relative place-content-center">
                <div className="inline-block">{props.value}</div>
                <div className="text-white text-xs text-center h-0">{props.subTitle}</div>
            </div>
            <div className="text-primary-green text-md text-center h-1/4">{props.title}</div>
        </div>
    );
}

export default NumberCard;