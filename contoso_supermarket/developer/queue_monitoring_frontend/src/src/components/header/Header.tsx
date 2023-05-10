import React from "react";
import { IconAlert, IconLogo, IconProfile, bgWood } from "../../images";
import { Link, useLocation } from "react-router-dom";
import { getEnvVariable } from "../../helpers/EnvHelper";

function Header() {
    //get the location from react router
    //used to determine which page is active
    const location = useLocation();
    const liveViewEnabled = getEnvVariable("REACT_APP_LIVE_VIEW_ENABLED")?.toLowerCase() === "true";

    //get the classes for the nav links based on the current path
    const getNavClasses = (path: string, disabled: boolean = false) => {
        if (disabled) {
            return "nav-link p-0 fs-5 text-muted disabled";
        } else if (location.pathname === path) {
            return "nav-link p-0 fs-5 text-primary";
        } else {
            return "nav-link p-0 fs-5 text-white";
        }
    };

    return (
        <nav
            className="navbar sticky-top navbar-expand-lg px-4"
            data-bs-theme="light"
            style={{ backgroundImage: `url(${bgWood})` }}
        >
            <div className="container-fluid">
                <Link className="navbar-brand p-3" to="/">
                    <IconLogo className="d-inline-block align-top" />
                </Link>
                <button
                    className="navbar-toggler navbar-dark"
                    type="button"
                    data-bs-toggle="collapse"
                    data-bs-target="#navbarSupportedContent"
                    aria-controls="navbarSupportedContent"
                    aria-expanded="false"
                    aria-label="Toggle navigation"
                >
                    <span className="navbar-toggler-icon"></span>
                </button>
                <div className="collapse navbar-collapse mb-4 mb-lg-0" id="navbarSupportedContent">
                    <div className="me-auto mb-2 mb-lg-0">
                        <div className="text-white fs-2 fw-normal">Managers Control Center</div>
                        <ul className="navbar-nav">
                            <li className="nav-item my-2 my-lg-0">
                                <Link className={getNavClasses("/")} to="/">
                                    Monitoring
                                </Link>
                            </li>
                            <li className="nav-item ms-0 ms-lg-4 my-2 my-lg-0">
                                <Link className={getNavClasses("/products")} to="/products">
                                    Products
                                </Link>
                            </li>
                            <li className="nav-item ms-0 ms-lg-4 my-2 my-lg-0">
                                <Link
                                    className={getNavClasses("/live-video", !liveViewEnabled)}
                                    to={liveViewEnabled ? "/live-video" : "#"}
                                >
                                    Live View
                                </Link>
                            </li>
                        </ul>
                    </div>
                    <div className="d-none d-lg-block">
                        <IconAlert />
                        <IconProfile className="ms-4" />
                    </div>
                </div>
            </div>
        </nav>
    );
}

export default Header;
