import { createBrowserRouter, RouterProvider } from "react-router-dom";
import MonitoringPage from "./pages/MonitoringPage";
import { GlobalProvider } from "./providers/GlobalContext";
import ProductsPage from "./pages/ProductsPage";
import LiveVideoPage from "./pages/LiveVideoPage";

const router = createBrowserRouter([
    {
        path: "/",
        element: <MonitoringPage />,
    },
    {
        path: "/products",
        element: <ProductsPage />,
    },
    {
        path: "/live-video",
        element: <LiveVideoPage />,
    },
]);

function App() {
    return (
        <GlobalProvider>
            <RouterProvider router={router} />
        </GlobalProvider>
    );
}

export default App;
