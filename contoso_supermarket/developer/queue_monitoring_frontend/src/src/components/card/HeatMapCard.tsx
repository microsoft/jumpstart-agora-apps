import React from "react";
import { CheckoutHistory, CheckoutType, useGlobalContext } from "../../providers/GlobalContext";
import { ExpressCheckout, SelfCheckout, StandardCheckout } from "../../images";

interface HeatMapCardProps {
    className?: string;
    checkoutHistory: CheckoutHistory[];
    isLoading: boolean;
}

const getCheckoutImage = (checkoutType: CheckoutType) => {
    switch (checkoutType) {
        case CheckoutType.Standard:
            return <StandardCheckout className="mw-100" style={{ width: "90%" }} />;
        case CheckoutType.Express:
            return <ExpressCheckout className="mw-100" style={{ width: "75%" }} />;
        case CheckoutType.SelfService:
            return <SelfCheckout className="mw-100" style={{ width: "60%" }} />;
    }
};

const getCheckoutColorClass = (item: CheckoutHistory, isClosed: boolean) => {
    const waitTimeMins = item.averageWaitTimeSeconds / 60;
    if (isClosed) {
        return "bg-secondary-light text-white";
    } else if (waitTimeMins <= 2) {
        return "bg-success";
    } else if (waitTimeMins <= 4) {
        return "bg-warning";
    } else {
        return "bg-danger text-white";
    }
};

const getCheckoutLabelText = (checkoutType: CheckoutType) => {
    switch (checkoutType) {
        case CheckoutType.Standard:
            return "Checkout";
        case CheckoutType.Express:
            return "Express";
        case CheckoutType.SelfService:
            return "Self-Service";
    }
};

function HeatMapCard(props: HeatMapCardProps) {
    const { checkouts, toggleCheckout } = useGlobalContext();

    return (
        <div className={"" + props.className}>
            <div className="row">
                {props.checkoutHistory.map((item) => {
                    const checkout = checkouts?.filter((c) => c.id === item.checkoutId)[0];
                    if (!checkout) {
                        return <div key={item.checkoutId}></div>;
                    }
                    return (
                        <div key={item.checkoutId} className="col d-flex flex-column">
                            <div className="d-flex justify-content-end pb-4">
                                <button
                                    className={"btn text-white " + (checkout.closed ? " bg-danger" : " bg-primary")}
                                    onClick={() => toggleCheckout && toggleCheckout(checkout.id, item.timestamp)}
                                >
                                    {checkout.closed ? "Closed" : "Open"}
                                </button>
                            </div>
                            <div className="flex-grow-1 d-flex align-items-center row">
                                <div className="col-4 d-flex flex-column position-relative h-100">
                                    {!props.isLoading &&
                                        Array(item.queueLength)
                                            .fill(0)
                                            .map((x, i) => {
                                                return (
                                                    <div
                                                        key={i}
                                                        style={{
                                                            position: "absolute",
                                                            background: "#08dde5",
                                                            border: "1px white solid",
                                                            height: "1.25rem",
                                                            width: "1.25rem",
                                                            borderRadius: "100%",
                                                            left: `calc(${Math.floor(Math.random() * 100)}%)`,
                                                            top: `${Math.floor(Math.random() * 90)}%`,
                                                        }}
                                                    ></div>
                                                );
                                            })}
                                </div>
                                <div className="col-8 text-end">{getCheckoutImage(item.checkoutType)}</div>
                            </div>
                            <div
                                className={
                                    "d-flex justify-content-between align-items-center rounded-1 position-relative mt-4 fw-semibold " +
                                    getCheckoutColorClass(item, checkout.closed)
                                }
                            >
                                <div className="fs-6 ms-4">
                                    {getCheckoutLabelText(item.checkoutType)} {item.checkoutId}
                                </div>
                                <div className="fs-3 me-4">{item.queueLength}</div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

export default HeatMapCard;
