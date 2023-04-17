import React from 'react';
import { bgWood, header } from "../../images";

function Header() {
    return (
        <>
            <img
                className=""
                src={header} alt="header"
            />
            <div

                className={"justify-center bg-no-repeat bg-cover bg-center"}
                style={{ backgroundImage: `url(${bgWood})` }}
            >

            </div>
        </>

    );
}

export default Header;