import React, { useEffect } from 'react';
import WaitTimeGraph from "../components/graphs/WaitTimeGraph";
import { CheckoutType, useGlobalContext } from "../providers/GlobalContext";
import dayjs from 'dayjs';
import NumberCard from "../components/card/NumberCard";
import Header from "../components/header/Header";

function ManagerPortal() {
    const { getCheckoutHistory, checkoutHistory } = useGlobalContext();

    //initial data load
    useEffect(() => {
        const yesterday = dayjs().add(-1, 'day').startOf('day');
        getCheckoutHistory && getCheckoutHistory(yesterday.toDate());
    }, [getCheckoutHistory]);

    const latestTimestamp = checkoutHistory?.reduce((acc, curr) => dayjs(curr.timestamp).isAfter(dayjs(acc)) ? curr.timestamp : acc, checkoutHistory[0]?.timestamp);
    const latestCheckoutHistory = checkoutHistory?.filter(history => history.timestamp === latestTimestamp);

    const totalPeople = latestCheckoutHistory?.reduce((acc, curr) => acc + curr.queueLength, 0) ?? 0;

    const expressCheckouts = latestCheckoutHistory?.filter(history => history.checkoutType === CheckoutType.Express);
    const expressPeople = expressCheckouts?.reduce((acc, curr) => acc + curr.queueLength, 0);
    const expressAvgWaitTime = expressCheckouts?.reduce((acc, curr) => acc + curr.averageWaitTimeSeconds, 0) / expressCheckouts.length / 60;

    const standardCheckouts = latestCheckoutHistory?.filter(history => history.checkoutType === CheckoutType.Standard);
    const standardPeople = standardCheckouts?.reduce((acc, curr) => acc + curr.queueLength, 0);
    const standardAvgWaitTime = standardCheckouts?.reduce((acc, curr) => acc + curr.averageWaitTimeSeconds, 0) / standardCheckouts.length / 60;

    const selfServiceCheckouts = latestCheckoutHistory?.filter(history => history.checkoutType === CheckoutType.SelfService);
    const selfServicePeople = selfServiceCheckouts?.reduce((acc, curr) => acc + curr.queueLength, 0);
    const selfServiceAvgWaitTime = selfServiceCheckouts?.reduce((acc, curr) => acc + curr.averageWaitTimeSeconds, 0) / selfServiceCheckouts.length / 60;

    const formatNumber = (num: Number) => {
        return num.toLocaleString(dayjs.locale(), {
            minimumFractionDigits: 0,
            maximumFractionDigits: 1,
        });
    };

    return (
        <>
            <Header />
            <div className="flex flex-col py-4 px-8 sm:px-8">
                <h1 className="text-primary-green text-2xl mb-2">Checkout Queue Monitoring</h1>
                <div className="flex flex-col mb-4">
                    <div className="text-primary-green text-lg mb-1">Checkout Heatmap</div>
                    <div className="w-full h-full border-secondary-grey border-[0.5rem] md:border-[1rem] aspect-[16/6] bg-[#6b6b6b]" />
                </div>
                <div className="grid grid-cols-6 gap-4 lg:flex">
                    <div className="col-span-6 sm:col-span-3 lg:w-1/4">
                        <div className="text-primary-green text-lg mb-1">Checkout Queue Report</div>
                        <div className="grid grid-cols-2 gap-4">
                            <NumberCard className="bg-secondary-grey aspect-square" title="Total People" value={totalPeople.toString()} />
                            <NumberCard className="bg-secondary-grey aspect-square" title="Express" value={expressPeople.toString()} />
                            <NumberCard className="bg-secondary-grey aspect-square" title="Checkout" value={standardPeople.toString()} />
                            <NumberCard className="bg-secondary-grey aspect-square" title="Self Service" value={selfServicePeople.toString()} />
                        </div>
                    </div>
                    <div className="col-span-6 sm:col-span-3 lg:w-1/4">
                        <div className="text-primary-green text-lg mb-1">Checkout Wait Report</div>
                        <div className="grid grid-cols-2 gap-4">
                            <NumberCard className="bg-secondary-grey aspect-square" title="Avg Wait Time" value={formatNumber(expressAvgWaitTime)} subTitle="mins" />
                            <NumberCard className="bg-secondary-grey aspect-square" title="Express" value={formatNumber(expressAvgWaitTime)} subTitle="mins" />
                            <NumberCard className="bg-secondary-grey aspect-square" title="Checkout" value={formatNumber(standardAvgWaitTime)} subTitle="mins" />
                            <NumberCard className="bg-secondary-grey aspect-square" title="Self Service" value={formatNumber(selfServiceAvgWaitTime)} subTitle="mins" />
                        </div>
                    </div>
                    <div className="col-span-6 sm:col-span-6 lg:w-1/2">
                        <div className="text-primary-green text-lg mb-1">Wait Time</div>
                        <div className="bg-secondary-grey aspect-[4/3] md:aspect-[2]">
                            <WaitTimeGraph checkoutHistory={checkoutHistory} />
                        </div>
                    </div>
                </div>
            </div>
        </>

    );
}

export default ManagerPortal;