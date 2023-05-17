import React, { useEffect, useState } from "react";
import { CheckoutHistory, CheckoutType } from "../../providers/GlobalContext";
import {
    ResponsiveContainer,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    Label,
    TooltipProps,
} from "recharts";
import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";
dayjs.extend(utc);
dayjs.extend(timezone);

interface AggregatedDataItem {
    timestamp: string;
    selfCheckoutWaitTime: number;
    expressCheckoutWaitTime: number;
    standardCheckoutWaitTime: number;
}

const formatXAxis = (tickItem: string | number | Date) => {
    return dayjs(tickItem).utc().format("hh.mm A");
};

const CustomTooltip = (props: TooltipProps<any, string>) => {
    const { active, payload, label } = props;

    if (active && payload && payload.length) {
        const formattedDate = dayjs(label).utc().format("MM/DD/YYYY hh:mm A");
        return (
            <div className="bg-white p-3">
                <div className="d-flex justify-content-between fs-7">
                    <span>Timestamp:</span>
                    <span className="ps-3">{formattedDate}</span>
                </div>
                {payload.map((item) => (
                    <div key={item.name} className="d-flex justify-content-between fs-7">
                        <span>{item.name}:</span>
                        <span>{item.value} mins</span>
                    </div>
                ))}
            </div>
        );
    }
    return null;
};

const aggregateData = (checkoutHistory: CheckoutHistory[]): AggregatedDataItem[] => {
    if (checkoutHistory.length === 0) {
        return [];
    }
    const aggregatedData = new Map<string, AggregatedDataItem>();
    const fiveMinutesInMs = 5 * 60 * 1000;

    // Find the first and last timestamp in the data
    const firstTimestamp = checkoutHistory.reduce(
        (min, p) => (p.timestamp < min ? p.timestamp : min),
        checkoutHistory[0].timestamp
    );
    const lastTimestamp = checkoutHistory.reduce(
        (max, p) => (p.timestamp > max ? p.timestamp : max),
        checkoutHistory[0].timestamp
    );

    // Loop through every 5-minute period between the first and last timestamp
    for (
        let currentTimestamp = new Date(firstTimestamp).getTime();
        currentTimestamp <= new Date(lastTimestamp).getTime();
        currentTimestamp += fiveMinutesInMs
    ) {
        const fiveMinuteTimestamp = Math.floor(currentTimestamp / fiveMinutesInMs) * fiveMinutesInMs;
        const timestampISO = new Date(fiveMinuteTimestamp).toISOString();
        if (!aggregatedData.has(timestampISO)) {
            aggregatedData.set(timestampISO, {
                timestamp: timestampISO,
                selfCheckoutWaitTime: 0,
                expressCheckoutWaitTime: 0,
                standardCheckoutWaitTime: 0,
            });
        }
    }

    checkoutHistory.forEach((checkout) => {
        const timestamp = new Date(checkout.timestamp).getTime();
        const fiveMinuteTimestamp = Math.floor(timestamp / fiveMinutesInMs) * fiveMinutesInMs;
        const timestampISO = new Date(fiveMinuteTimestamp).toISOString();
        const aggregatedDataItem = aggregatedData.get(timestampISO)!;
        if (!!aggregatedDataItem) {
            if (checkout.averageWaitTimeSeconds === 0) {
                return;
            }
            switch (checkout.checkoutType) {
                case CheckoutType.SelfService:
                    aggregatedDataItem.selfCheckoutWaitTime = checkout.averageWaitTimeSeconds / 60;
                    break;
                case CheckoutType.Express:
                    aggregatedDataItem.expressCheckoutWaitTime = checkout.averageWaitTimeSeconds / 60;
                    break;
                case CheckoutType.Standard:
                    aggregatedDataItem.standardCheckoutWaitTime = checkout.averageWaitTimeSeconds / 60;
                    break;
            }
        }
    });

    return Array.from(aggregatedData.values());
};

interface WaitTimeGraphProps {
    checkoutHistory: CheckoutHistory[];
}

function WaitTimeGraph(props: WaitTimeGraphProps) {
    const [aggregatedCheckoutHistory, setAggregatedCheckoutHistory] = useState<AggregatedDataItem[]>([]);

    useEffect(() => {
        const agg = aggregateData(props.checkoutHistory);
        setAggregatedCheckoutHistory(agg);
    }, [props.checkoutHistory]);

    return (
        <ResponsiveContainer width="99%" height="99%">
            <LineChart
                data={aggregatedCheckoutHistory}
                margin={{ top: 0, right: 20, bottom: -10, left: -15 }}
                className="bg-secondary"
            >
                <CartesianGrid strokeDasharray="0" vertical={false} horizAdvX={1} />
                <XAxis
                    dataKey="timestamp"
                    tickFormatter={formatXAxis}
                    height={40}
                    tick={{ dy: 10, fontWeight: "400", fontSize: "0.75rem", fill: "#FFF" }}
                    interval={59}
                />
                <YAxis
                    yAxisId="left"
                    tick={{ fontWeight: "400", fontSize: "0.75rem", fill: "#FFF" }}
                    domain={[0, "auto"]}
                >
                    <Label
                        value="Wait Time (mins)"
                        angle={-90}
                        position="insideLeft"
                        offset={25}
                        style={{ fontWeight: "500", fontSize: "0.75rem", fill: "#FFF", textAnchor: "middle" }}
                    />
                </YAxis>
                <Tooltip content={<CustomTooltip />} />
                <Legend iconSize={0} wrapperStyle={{ fontSize: "0.8rem" }} />
                <Line
                    yAxisId="left"
                    name="Standard"
                    type="monotone"
                    dataKey="standardCheckoutWaitTime"
                    isAnimationActive={false}
                    stroke="#BB80ff"
                    dot={false}
                />
                <Line
                    yAxisId="left"
                    name="Express"
                    type="monotone"
                    dataKey="expressCheckoutWaitTime"
                    isAnimationActive={false}
                    stroke="#f5f73e"
                    dot={false}
                />
                <Line
                    yAxisId="left"
                    name="Self Service"
                    type="monotone"
                    dataKey="selfCheckoutWaitTime"
                    isAnimationActive={false}
                    stroke="#2be6e6"
                    dot={false}
                />{" "}
            </LineChart>
        </ResponsiveContainer>
    );
}

export default WaitTimeGraph;
