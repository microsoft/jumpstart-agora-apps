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

export interface GlobalContextInterface {
    //checkout history
    checkoutHistory: CheckoutHistory[];
    getCheckoutHistory?: (startDate?: Date, endDate?: Date) => void;
    checkoutHistoryLoading: boolean;

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
    productsLoading: false,
    checkoutHistoryLoading: false,
});

export const GlobalProvider = ({ children }: { children: React.ReactNode }) => {
    const [checkoutHistory, setCheckoutHistory] = useState<CheckoutHistory[]>([]);
    const [checkoutHistoryLoading, setCheckoutHistoryLoading] = useState<boolean>(false);

    const [products, setProducts] = useState<Product[]>([]);
    const [productsLoading, setProductsLoading] = useState<boolean>(false);

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
            }}
        >
            {children}
        </GlobalContext.Provider>
    );
};

export const useGlobalContext = () => useContext(GlobalContext);
