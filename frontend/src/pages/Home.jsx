import { useState } from "react";
import MainLayout from "../layout/MainLayout";
import LandingPage from "./Landing/LandingPage";

export default function Home() {
    const [hasEntered, setHasEntered] = useState(false);

    if (!hasEntered) {
        return <LandingPage onComplete={() => setHasEntered(true)} />;
    }

    return <MainLayout />;
}