import React from "react";
import { IconAlert, IconLogo, IconProfile, bgWood } from "../../images";
import { useLocation } from "react-router-dom";

function Header() {
    //get the location from react router
    //used to determine which page is active
    const location = useLocation();

    //get the classes for the nav links based on the current path
    const getNavClasses = (path: string) => {
        if (location.pathname === path) {
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
                <a className="navbar-brand p-3" href="{{ url_for('index') }}">
                    <IconLogo className="d-inline-block align-top" />
                </a>
                <button
                    className="navbar-toggler"
                    type="button"
                    data-bs-toggle="collapse"
                    data-bs-target="#navbarSupportedContent"
                    aria-controls="navbarSupportedContent"
                    aria-expanded="false"
                    aria-label="Toggle navigation"
                >
                    <span className="navbar-toggler-icon"></span>
                </button>
                <div className="collapse navbar-collapse" id="navbarSupportedContent">
                    <div className="me-auto mb-2 mb-lg-0">
                        <div className="text-white fs-1 fw-normal">Managers Control Center</div>
                        <ul className="navbar-nav">
                            <li className="nav-item">
                                <a className={getNavClasses("/")} href="/">
                                    Monitoring
                                </a>
                            </li>
                            <li className="nav-item ms-4">
                                <a className={getNavClasses("/products")} href="/products">
                                    Products
                                </a>
                            </li>
                            <li className="nav-item ms-4">
                                <a className={getNavClasses("/live-View")} href="/live-view">
                                    Live View
                                </a>
                            </li>
                        </ul>
                    </div>
                    <div>
                        <IconAlert />
                        <IconProfile className="ms-4" />
                    </div>
                </div>
            </div>
        </nav>
    );
}

export default Header;
