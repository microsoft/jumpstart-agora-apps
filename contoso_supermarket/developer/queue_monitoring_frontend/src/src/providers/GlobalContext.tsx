import * as React from "react";
import { createContext, useCallback, useContext, useState } from "react";
import axios from "axios";
import dayjs from "dayjs";
import { toast } from "react-toastify";

export enum CheckoutType {
    Standard = 1,
    Express = 2,
    SelfService = 3,
}

export interface CheckoutHistory {
    timestamp: string;
    checkoutId: number;
    checkoutType: CheckoutType;
    queueLength: number;
    averageWaitTimeSeconds: number;
}

export interface Product {
    id: number;
    name: string;
    price: number;
    description: string;
    photoPath: string;
    stock: number;
}

export interface Checkout {
    id: number;
    type: CheckoutType;
    avgProcessingTime: number;
    closed: boolean;
}

export interface GlobalContextInterface {
    //checkout history
    checkoutHistory: CheckoutHistory[];
    getCheckoutHistory?: (startDate?: Date, endDate?: Date) => void;
    checkoutHistoryLoading: boolean;

    //checkouts
    getCheckouts?: () => void;
    toggleCheckout?: (checkoutId: number, timestamp: string) => void;
    checkoutsLoading: boolean;
    checkouts: Checkout[];

    //products
    products: Product[];
    getProducts?: () => void;
    updateProducts?: (products: Product[]) => void;
    deleteProduct?: (productId: number) => void;
    productsLoading: boolean;
}

export const GlobalContext = createContext<GlobalContextInterface>({
    checkoutHistory: [],
    products: [],
    checkouts: [],
    productsLoading: false,
    checkoutHistoryLoading: false,
    checkoutsLoading: false,
});

export const GlobalProvider = ({ children }: { children: React.ReactNode }) => {
    const [checkoutHistory, setCheckoutHistory] = useState<CheckoutHistory[]>([]);
    const [checkoutHistoryLoading, setCheckoutHistoryLoading] = useState<boolean>(false);

    const [products, setProducts] = useState<Product[]>([]);
    const [productsLoading, setProductsLoading] = useState<boolean>(false);

    const [checkouts, setCheckouts] = useState<Checkout[]>([]);
    const [checkoutsLoading, setCheckoutsLoading] = useState<boolean>(false);

    const getCheckouts = useCallback(() => {
        setCheckoutsLoading(true);
        //get checkout status
        axios
            .get(`/api/checkouts`)
            .then((ret) => {
                setCheckouts(ret.data);
            })
            .finally(() => {
                setCheckoutsLoading(false);
            });
    }, []);

    const getCheckoutHistory = useCallback((startDate?: Date, endDate?: Date) => {
        setCheckoutHistoryLoading(true);
        //get checkoutHistory
        axios
            .get(
                `/api/checkoutHistory${!!startDate || !!endDate ? "?" : ""}${
                    !!startDate ? "startDate=" + startDate.toISOString() : ""
                }${!!endDate ? "endDate=" + endDate.toISOString() : ""}`
            )
            .then((ret) => {
                setCheckoutHistory((results) => {
                    const oldResults =
                        results?.filter(
                            (r) =>
                                !ret.data.some(
                                    (newR: CheckoutHistory) =>
                                        newR.checkoutId === r.checkoutId && newR.timestamp === r.timestamp
                                )
                        ) ?? [];
                    return oldResults
                        .concat(ret.data)
                        .sort((a, b) => (dayjs(b.timestamp).isAfter(dayjs(a.timestamp)) ? 1 : -1));
                });
            })
            .finally(() => {
                setCheckoutHistoryLoading(false);
            });
    }, []);

    const toggleCheckout = useCallback((checkoutId: number, timestamp: string) => {
        setCheckoutsLoading(true);
        //close/open checkout
        axios
            .get(`/api/checkouts/${checkoutId}/toggle`)
            .then((ret) => {
                setCheckouts((results) => {
                    const checkout: Checkout = ret.data;
                    const index = results.findIndex((c) => c.id === checkout.id);
                    if (index >= 0) {
                        // Update existing checkout
                        const updatedResults = [...results];
                        updatedResults[index] = checkout;
                        return updatedResults;
                    } else {
                        // Insert new checkout
                        return [...results, checkout];
                    }
                });
            })
            .finally(() => {
                setCheckoutsLoading(false);
                getCheckoutHistory(new Date(timestamp));
            });
    }, [getCheckoutHistory]);

    const getProducts = useCallback(() => {
        setProductsLoading(true);
        //get products
        axios
            .get(`/api/products`)
            .then((ret) => {
                setProducts(ret.data);
            })
            .finally(() => {
                setProductsLoading(false);
            });
    }, []);

    const updateProducts = useCallback((products: Product[]) => {
        //update products
        axios
            .post(`/api/products`, JSON.stringify(products), {
                headers: {
                    "Content-Type": "application/json",
                },
            })
            .then(() => {
                toast.success("Products updated successfully...");
            })
            .catch(() => {
                toast.error("Failed to update products...");
            });
    }, []);

    const deleteProduct = useCallback((productId: number) => {
        //delete product
        axios
            .delete(`/api/products/${productId}`)
            .then(() => {
                setProducts((x) => x.filter((item) => item.id !== productId));
                toast.success(`Product '${productId}' was deleted successfully...`);
            })
            .catch(() => {
                toast.error("Failed to delete product...");
            });
    }, []);

    return (
        <GlobalContext.Provider
            value={{
                checkoutHistory: checkoutHistory,
                checkoutHistoryLoading: checkoutHistoryLoading,
                getCheckoutHistory: getCheckoutHistory,
                products: products,
                productsLoading: productsLoading,
                getProducts: getProducts,
                updateProducts: updateProducts,
                deleteProduct: deleteProduct,
                getCheckouts: getCheckouts,
                checkoutsLoading: checkoutsLoading,
                toggleCheckout: toggleCheckout,
                checkouts: checkouts,
            }}
        >
            {children}
        </GlobalContext.Provider>
    );
};

export const useGlobalContext = () => useContext(GlobalContext);
