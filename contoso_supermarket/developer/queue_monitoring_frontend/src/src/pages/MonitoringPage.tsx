import React, { useEffect } from "react";
import WaitTimeGraph from "../components/graphs/WaitTimeGraph";
import { Checkout, CheckoutType, useGlobalContext } from "../providers/GlobalContext";
import dayjs from "dayjs";
import Header from "../components/header/Header";
import ReportCard from "../components/card/ReportCard";
import HeatMapCard from "../components/card/HeatMapCard";

function countOpenCheckouts(checkouts: Checkout[]): number {
    const openCheckoutsPerType = Object.assign({}, ...Object.values(CheckoutType).map((type) => ({ [type]: false })));
    for (const checkout of checkouts) {
        if (!checkout.closed) {
            openCheckoutsPerType[checkout.type] = true;
        }
    }
    return Object.values(openCheckoutsPerType).filter(Boolean).length;
}
function MonitoringPage() {
    const { getCheckoutHistory, checkoutHistory, checkoutHistoryLoading, checkouts, getCheckouts } = useGlobalContext();

    //initial data load
    useEffect(() => {
        const yesterday = dayjs().add(-1, "day");
        getCheckoutHistory && getCheckoutHistory(yesterday.toDate());
    }, [getCheckoutHistory]);

    useEffect(() => {
        if (checkouts.length === 0 && getCheckouts) {
            getCheckouts();
        }
    }, [checkouts, getCheckouts]);

    const latestTimestamp = checkoutHistory?.reduce(
        (acc, curr) => (dayjs(curr.timestamp).isAfter(dayjs(acc)) ? curr.timestamp : acc),
        checkoutHistory[0]?.timestamp
    );

    //get new checkout data every minute
    useEffect(() => {
        const intervalId = setInterval(() => {
            if (latestTimestamp !== undefined && !!latestTimestamp.length && getCheckoutHistory && getCheckouts) {
                getCheckoutHistory(new Date(latestTimestamp));
                getCheckouts();
            }
        }, 60000);

        // Clear interval on component unmount
        return () => clearInterval(intervalId);
    }, [latestTimestamp, getCheckoutHistory, getCheckouts]);

    const openCheckouts = countOpenCheckouts(checkouts);

    const latestCheckoutHistory = checkoutHistory?.filter((history) => history.timestamp === latestTimestamp);
    const latestCheckoutHistoryOrderedByType = latestCheckoutHistory.sort((a, b) => a.checkoutId - b.checkoutId);

    const totalPeople = latestCheckoutHistory?.reduce((acc, curr) => acc + curr.queueLength, 0) ?? 0;

    const expressCheckouts = latestCheckoutHistory?.filter(
        (history) =>
            history.checkoutType === CheckoutType.Express &&
            checkouts.find((x) => x.id === history.checkoutId)?.closed === false
    );
    const expressPeople = expressCheckouts?.reduce((acc, curr) => acc + curr.queueLength, 0);
    const expressAvgWaitTime =
        expressCheckouts.length === 0
            ? 0
            : expressCheckouts?.reduce((acc, curr) => acc + curr.averageWaitTimeSeconds, 0) /
              expressCheckouts.length /
              60;

    const standardCheckouts = latestCheckoutHistory?.filter(
        (history) =>
            history.checkoutType === CheckoutType.Standard &&
            checkouts.find((x) => x.id === history.checkoutId)?.closed === false
    );
    const standardPeople = standardCheckouts?.reduce((acc, curr) => acc + curr.queueLength, 0);
    const standardAvgWaitTime =
        standardCheckouts?.length === 0
            ? 0
            : standardCheckouts?.reduce((acc, curr) => acc + curr.averageWaitTimeSeconds, 0) /
              standardCheckouts.length /
              60;

    const selfServiceCheckouts = latestCheckoutHistory?.filter(
        (history) =>
            history.checkoutType === CheckoutType.SelfService &&
            checkouts.find((x) => x.id === history.checkoutId)?.closed === false
    );
    const selfServicePeople = selfServiceCheckouts?.reduce((acc, curr) => acc + curr.queueLength, 0);
    const selfServiceAvgWaitTime =
        selfServiceCheckouts?.length === 0
            ? 0
            : selfServiceCheckouts?.reduce((acc, curr) => acc + curr.averageWaitTimeSeconds, 0) /
              selfServiceCheckouts.length /
              60;

    const avgWaitTime =
        openCheckouts === 0 ? 0 : (expressAvgWaitTime + standardAvgWaitTime + selfServiceAvgWaitTime) / openCheckouts;

    const standardAllClosed = checkouts
        .filter((x) => x.type === CheckoutType.Standard)
        .every((checkout) => checkout.closed);
    const expressAllClosed = checkouts
        .filter((x) => x.type === CheckoutType.Express)
        .every((checkout) => checkout.closed);
    const selfServiceAllClosed = checkouts
        .filter((x) => x.type === CheckoutType.SelfService)
        .every((checkout) => checkout.closed);

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
                                standardThresholdValue={standardAvgWaitTime}
                                selfServiceThresholdValue={selfServiceAvgWaitTime}
                                expressThresholdValue={expressAvgWaitTime}
                                standardClosed={standardAllClosed}
                                expressClosed={expressAllClosed}
                                selfServiceClosed={selfServiceAllClosed}
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
                                standardThresholdValue={standardAvgWaitTime}
                                selfServiceThresholdValue={selfServiceAvgWaitTime}
                                expressThresholdValue={expressAvgWaitTime}
                                standardClosed={standardAllClosed}
                                expressClosed={expressAllClosed}
                                selfServiceClosed={selfServiceAllClosed}
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
