import React, { useEffect } from "react";
import WaitTimeGraph from "../components/graphs/WaitTimeGraph";
import { CheckoutType, useGlobalContext } from "../providers/GlobalContext";
import dayjs from "dayjs";
import Header from "../components/header/Header";
import ReportCard from "../components/card/ReportCard";
import HeatMapCard from "../components/card/HeatMapCard";

function MonitoringPage() {
    const { getCheckoutHistory, checkoutHistory } = useGlobalContext();

    //initial data load
    useEffect(() => {
        const yesterday = dayjs().add(-1, "day").startOf("day");
        getCheckoutHistory && getCheckoutHistory(yesterday.toDate());
    }, [getCheckoutHistory]);

    const latestTimestamp = checkoutHistory?.reduce(
        (acc, curr) => (dayjs(curr.timestamp).isAfter(dayjs(acc)) ? curr.timestamp : acc),
        checkoutHistory[0]?.timestamp
    );

    //get new checkout data every minute
    useEffect(() => {
        const intervalId = setInterval(() => {
            if (!!latestTimestamp.length) {
                getCheckoutHistory && getCheckoutHistory(new Date(latestTimestamp));
            }
        }, 60000);

        // Clear interval on component unmount
        return () => clearInterval(intervalId);
    }, [latestTimestamp]);

    const latestCheckoutHistory = checkoutHistory?.filter((history) => history.timestamp === latestTimestamp);
    const latestCheckoutHistoryOrderedByType = latestCheckoutHistory.sort(
        (a, b) => a.checkoutType - b.checkoutType || a.checkoutId - b.checkoutId
    );

    const totalPeople = latestCheckoutHistory?.reduce((acc, curr) => acc + curr.queueLength, 0) ?? 0;

    const expressCheckouts = latestCheckoutHistory?.filter((history) => history.checkoutType === CheckoutType.Express);
    const expressPeople = expressCheckouts?.reduce((acc, curr) => acc + curr.queueLength, 0);
    const expressAvgWaitTime =
        expressCheckouts?.reduce((acc, curr) => acc + curr.averageWaitTimeSeconds, 0) / expressCheckouts.length / 60;

    const standardCheckouts = latestCheckoutHistory?.filter(
        (history) => history.checkoutType === CheckoutType.Standard
    );
    const standardPeople = standardCheckouts?.reduce((acc, curr) => acc + curr.queueLength, 0);
    const standardAvgWaitTime =
        standardCheckouts?.reduce((acc, curr) => acc + curr.averageWaitTimeSeconds, 0) / standardCheckouts.length / 60;

    const selfServiceCheckouts = latestCheckoutHistory?.filter(
        (history) => history.checkoutType === CheckoutType.SelfService
    );
    const selfServicePeople = selfServiceCheckouts?.reduce((acc, curr) => acc + curr.queueLength, 0);
    const selfServiceAvgWaitTime =
        selfServiceCheckouts?.reduce((acc, curr) => acc + curr.averageWaitTimeSeconds, 0) /
        selfServiceCheckouts.length /
        60;

    const avgWaitTime = (expressAvgWaitTime + standardAvgWaitTime + selfServiceAvgWaitTime) / 3;

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

    return (
        <>
            <Header />
            <div className="flex flex-col py-4 px-8 px-sm-8 container">
                <h1 className="text-primary mb-2 fs-2">Checkout Queue Monitoring</h1>
                <div className="flex flex-col mb-4">
                    <div className="text-primary h4 mb-1">Checkout Heatmap</div>
                    <HeatMapCard className="" checkoutHistory={latestCheckoutHistoryOrderedByType} />
                </div>

                <div className="row">
                    <div className="col-12 col-md-6 col-lg-3">
                        <div className="h-100">
                            <div className="text-primary h4 mb-3">Queue Report</div>
                            <ReportCard
                                title="Total People"
                                value={totalPeople}
                                standardValue={standardPeople}
                                expressValue={expressPeople}
                                selfServiceValue={selfServicePeople}
                            />
                        </div>
                    </div>
                    <div className="col-12 col-md-6 col-lg-3 h-100">
                        <div className="h-100">
                            <div className="text-primary h4 mb-3">Wait Time Report</div>
                            <ReportCard
                                title="Average Wait Time"
                                value={formatNumber(avgWaitTime)}
                                unit="mins"
                                standardValue={formatNumber(standardAvgWaitTime)}
                                expressValue={formatNumber(expressAvgWaitTime)}
                                selfServiceValue={formatNumber(selfServiceAvgWaitTime)}
                            />
                        </div>
                    </div>
                    <div className="col-12 col-md-12 col-lg-6">
                        <div className="h-100 d-flex flex-column">
                            <div className="text-primary h4 mb-3">Wait Time</div>
                            <div className="bg-secondary rounded p-3 flex-grow-1">
                                <WaitTimeGraph checkoutHistory={checkoutHistory} />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}

export default MonitoringPage;