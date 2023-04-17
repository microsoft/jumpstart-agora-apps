import {
    createBrowserRouter,
    RouterProvider,
} from "react-router-dom";
import './App.css';
import ManagerPortal from "./pages/ManagerPortal";
import { GlobalProvider } from "./providers/GlobalContext";

const router = createBrowserRouter([
    {
        path: "/",
        element: <ManagerPortal />,
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
