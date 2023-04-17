import React, { useEffect, useState } from 'react';
import { CheckoutHistory, CheckoutType } from "../../providers/GlobalContext";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Label, TooltipProps } from 'recharts';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
dayjs.extend(utc);
dayjs.extend(timezone);

interface AggregatedDataItem {
    timestamp: string;
    selfCheckoutWaitTime: number;
    expressCheckoutWaitTime: number;
    standardCheckoutWaitTime: number;
}

const formatXAxis = (tickItem: string | number | Date) => {
    return dayjs(tickItem).format('hh.mm A');
};

const aggregateData = (checkoutHistory: CheckoutHistory[]): AggregatedDataItem[] => {
    if (checkoutHistory.length === 0) { return []; }
    const aggregatedData: AggregatedDataItem[] = [];
    const fiveMinutesInMs = 5 * 60 * 1000;

    // Find the first and last timestamp in the data
    const firstTimestamp = checkoutHistory.reduce((min, p) => p.timestamp < min ? p.timestamp : min, checkoutHistory[0].timestamp);
    const lastTimestamp = checkoutHistory.reduce((max, p) => p.timestamp > max ? p.timestamp : max, checkoutHistory[0].timestamp);

    // Loop through every 5-minute period between the first and last timestamp
    for (let currentTimestamp = new Date(firstTimestamp).getTime(); currentTimestamp <= new Date(lastTimestamp).getTime(); currentTimestamp += fiveMinutesInMs) {
        const fiveMinuteTimestamp = Math.floor(currentTimestamp / fiveMinutesInMs) * fiveMinutesInMs;
        let aggregatedDataItem = aggregatedData.find((item) => item.timestamp === new Date(fiveMinuteTimestamp).toISOString());

        if (!aggregatedDataItem) {
            aggregatedDataItem = {
                timestamp: new Date(fiveMinuteTimestamp).toISOString(),
                selfCheckoutWaitTime: 0,
                expressCheckoutWaitTime: 0,
                standardCheckoutWaitTime: 0,
            };
            aggregatedData.push(aggregatedDataItem);
        }
    }

    checkoutHistory.forEach((checkout) => {
        const timestamp = new Date(checkout.timestamp).getTime();
        const fiveMinuteTimestamp = Math.floor(timestamp / fiveMinutesInMs) * fiveMinutesInMs;
        let aggregatedDataItem = aggregatedData.find((item) => item.timestamp === new Date(fiveMinuteTimestamp).toISOString());

        if (!aggregatedDataItem) {
            // Handle the case where aggregatedDataItem is undefined
            // For example, you could create a new AggregatedDataItem object and add it to the array
            aggregatedDataItem = {
                timestamp: new Date(fiveMinuteTimestamp).toISOString(),
                selfCheckoutWaitTime: 0,
                expressCheckoutWaitTime: 0,
                standardCheckoutWaitTime: 0,
            };
            aggregatedData.push(aggregatedDataItem);
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
    });

    return aggregatedData;
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

    const CustomTooltip = (props: TooltipProps<any, string>) => {
        const { active, payload, label } = props;

        if (active && payload && payload.length) {
            const formattedDate = dayjs(label).format('MM/DD/YYYY HH:mm A');
            return (
                <div className="bg-white p-3 min-w-[300px]">
                    <div className="flex justify-between text-sm">
                        <span>Timestamp:</span>
                        <span>{formattedDate}</span>
                    </div>
                    {payload.map((item) => (
                        <div key={item.name} className="flex justify-between text-sm">
                            <span>{item.name}:</span>
                            <span>{item.value} mins</span>
                        </div>
                    ))}
                </div>
            );
        }
        return null;
    };

    return (
        <ResponsiveContainer width="99%" height="99%">
            <LineChart
                data={aggregatedCheckoutHistory}
                margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
                className="bg-[#313131]"
            >
                <CartesianGrid strokeDasharray="0" vertical={false} />
                <XAxis
                    dataKey="timestamp"
                    tickFormatter={formatXAxis}
                    textAnchor="beginning"
                    height={30}
                    tick={{ fontWeight: '400', fontSize: '0.75rem', fill: "#FFF" }}
                    interval={59}
                />
                <YAxis yAxisId="left"
                    tick={{ fontWeight: '400', fontSize: '0.75rem', fill: "#FFF" }}
                >
                    <Label
                        value="Wait Time (mins)"
                        angle={-90}
                        position="insideLeft"
                        offset={10}
                        style={{ fontWeight: '400', fill: "#FFF", textAnchor: 'middle' }}
                    />
                </YAxis>
                <Tooltip content={<CustomTooltip />} />
                <Legend

                    wrapperStyle={{ fontSize: "0.8rem" }} />

                <Line yAxisId="left" name="Self Checkout" type="monotone" dataKey="selfCheckoutWaitTime" stroke="#57b813" dot={false} />
                <Line yAxisId="left" name="Express Checkout" type="monotone" dataKey="expressCheckoutWaitTime" stroke="#f9ff01" dot={false} />
                <Line yAxisId="left" name="Standard Checkout" type="monotone" dataKey="standardCheckoutWaitTime" stroke="#f726f3" dot={false} />

            </LineChart>
        </ResponsiveContainer>
    );
}

export default WaitTimeGraph;