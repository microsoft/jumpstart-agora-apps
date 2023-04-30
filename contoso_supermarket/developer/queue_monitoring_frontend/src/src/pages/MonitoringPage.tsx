import React, { useEffect } from "react";
import WaitTimeGraph from "../components/graphs/WaitTimeGraph";
import { CheckoutType, useGlobalContext } from "../providers/GlobalContext";
import dayjs from "dayjs";
import Header from "../components/header/Header";
import ReportCard from "../components/card/ReportCard";
import HeatMapCard from "../components/card/HeatMapCard";

function MonitoringPage() {
    const { getCheckoutHistory, checkoutHistory, checkoutHistoryLoading } = useGlobalContext();

    //initial data load
    useEffect(() => {
        const yesterday = dayjs().add(-1, "day");
        getCheckoutHistory && getCheckoutHistory(yesterday.toDate());
    }, [getCheckoutHistory]);

    const latestTimestamp = checkoutHistory?.reduce(
        (acc, curr) => (dayjs(curr.timestamp).isAfter(dayjs(acc)) ? curr.timestamp : acc),
        checkoutHistory[0]?.timestamp
    );

    //get new checkout data every minute
    useEffect(() => {
        const intervalId = setInterval(() => {
            if (latestTimestamp !== undefined && !!latestTimestamp.length) {
                getCheckoutHistory && getCheckoutHistory(new Date(latestTimestamp));
            }
        }, 60000);

        // Clear interval on component unmount
        return () => clearInterval(intervalId);
    }, [latestTimestamp]);

    const latestCheckoutHistory = checkoutHistory?.filter((history) => history.timestamp === latestTimestamp);
    const latestCheckoutHistoryOrderedByType = latestCheckoutHistory.sort((a, b) => a.checkoutId - b.checkoutId);

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

    const totalStandardCheckouts =
        latestCheckoutHistory?.filter((history) => history.checkoutType === CheckoutType.Standard).length ?? 0;
    const totalExpressCheckouts =
        latestCheckoutHistory?.filter((history) => history.checkoutType === CheckoutType.Express).length ?? 0;
    const totalSelfServiceCheckouts =
        latestCheckoutHistory?.filter((history) => history.checkoutType === CheckoutType.SelfService).length ?? 0;

    return (
        <>
            <Header />
            <div className="flex flex-col py-4 px-8 px-sm-8 container">
                <h1 className="text-primary mb-2 fs-2">Checkout Queue Monitoring</h1>
                <div className="flex flex-col mb-4">
                    <div className="text-primary h4 mb-3">Checkout Heatmap</div>
                    <HeatMapCard
                        className="bg-secondary rounded p-3"
                        isLoading={checkoutHistoryLoading}
                        checkoutHistory={latestCheckoutHistoryOrderedByType}
                    />
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
                                expressThreshold={totalStandardCheckouts * 4}
                                standardThreshold={totalExpressCheckouts * 4}
                                selfServiceThreshold={totalSelfServiceCheckouts * 4}
                            />
                        </div>
                    </div>
                    <div className="col-12 col-md-6 col-lg-3 h-100">
                        <div className="h-100">
                            <div className="text-primary h4 mb-3">Wait Time Report</div>
                            <ReportCard
                                title="Average Wait Time"
                                value={avgWaitTime}
                                unit="mins"
                                standardValue={standardAvgWaitTime}
                                expressValue={expressAvgWaitTime}
                                selfServiceValue={selfServiceAvgWaitTime}
                                standardThreshold={(totalStandardCheckouts * 60 * 1) / 60}
                                expressThreshold={(totalSelfServiceCheckouts * 60 * 0.5) / 60}
                                selfServiceThreshold={(totalSelfServiceCheckouts * 60 * 0.7) / 60}
                            />
                        </div>
                    </div>
                    <div className="col-12 col-md-12 col-lg-6">
                        <div className="h-100 d-flex flex-column">
                            <div className="text-primary h4 mb-3">Shopper Wait Time (last 24 hours)</div>
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
