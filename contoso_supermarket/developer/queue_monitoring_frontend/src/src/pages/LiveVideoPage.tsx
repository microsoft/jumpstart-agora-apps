import React, { useEffect, useState } from "react";
import Header from "../components/header/Header";
import NumberCard from "../components/card/NumberCard";

function LiveVideoPage() {
    const [peopleCount, setPeopleCount] = useState(0);

    // Function to fetch the number of people in the store from the Flask backend
    const fetchPeopleCount = async () => {
        const response = await fetch("/ai/people_count");
        const count = await response.text();
        setPeopleCount(Number(count));
    };

    // Fetch the number of people in the store every second
    useEffect(() => {
        const interval = setInterval(fetchPeopleCount, 1000);
        return () => clearInterval(interval);
    }, []);

    return (
        <>
            <Header />
            <div className="flex flex-col py-4 px-8 px-sm-8 container">
                <h1 className="text-primary mb-2 fs-2">Video Feed</h1>
                <div className="row">
                    <div className="col-12 col-lg-10 mb-4">
                        <img src="/ai/video_feed" className="ratio ratio-16x9" alt="supermarket video feed" />
                    </div>
                    <div className="col-3 col-lg-2">
                        <NumberCard title={"People Count"} value={isNaN(peopleCount) ? 0 : peopleCount} />
                    </div>
                </div>
            </div>
        </>
    );
}

export default LiveVideoPage;
