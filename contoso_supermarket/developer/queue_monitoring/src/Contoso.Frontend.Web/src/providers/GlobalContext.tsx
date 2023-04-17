import * as React from "react";
import { createContext, useCallback, useContext, useState } from "react";
import axios from 'axios';
import dayjs from "dayjs";

export enum CheckoutType {
    Standard = 1,
    Express = 2,
    SelfService = 3
}

export interface CheckoutHistory {
    timestamp: string;
    checkoutId: number;
    checkoutType: CheckoutType;
    queueLength: number;
    averageWaitTimeSeconds: number;
}

export interface GlobalContextInterface {
    checkoutHistory: CheckoutHistory[];
    getCheckoutHistory?: (startDate?: Date, endDate?: Date) => void;
    checkoutHistoryLoading: boolean;
}

export const GlobalContext = createContext<GlobalContextInterface>({
    checkoutHistory: [],
    checkoutHistoryLoading: false
});

export const GlobalProvider = ({ children }: { children: React.ReactNode; }) => {
    const [checkoutHistory, setCheckoutHistory] = useState<CheckoutHistory[]>([]);
    const [checkoutHistoryLoading, setCheckoutHistoryLoading] = useState<boolean>(false);

    const getCheckoutHistory = useCallback((startDate?: Date, endDate?: Date) => {
        setCheckoutHistoryLoading(true);
        //get checkoutHistory
        axios
            .get(`/api/checkoutHistory${(!!startDate || !!endDate ? "?" : "")}${(!!startDate ? "startDate=" + startDate.toISOString() : "")}${(!!endDate ? "endDate=" + endDate.toISOString() : "")}`)
            .then((ret) => {
                setCheckoutHistory((results) => {
                    const oldResults = results?.filter(r => !ret.data.some((newR: CheckoutHistory) => newR.checkoutId === r.checkoutId && newR.timestamp === r.timestamp)) ?? [];
                    return oldResults.concat(ret.data).sort((a, b) => dayjs(b.timestamp).isAfter(dayjs(a.timestamp)) ? 1 : -1);
                });
            }).finally(() => {
                setCheckoutHistoryLoading(false);
            });
    }, []);

    return (
        <GlobalContext.Provider value={{
            checkoutHistory: checkoutHistory,
            checkoutHistoryLoading: checkoutHistoryLoading,
            getCheckoutHistory: getCheckoutHistory
        }}>
            {children}
        </GlobalContext.Provider>
    );
};

export const useGlobalContext = () => useContext(GlobalContext);