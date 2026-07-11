import { Box } from "@mui/material";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { FileText } from "lucide-react";

// Generate these outside the component to satisfy ESLint react-hooks/purity rules
const STARS = Array.from({ length: 150 }).map((_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 2 + 1,
    opacity: Math.random() * 0.8 + 0.2,
    duration: Math.random() * 3 + 2
}));

const PAPERS = Array.from({ length: 8 }).map((_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    scale: Math.random() * 0.5 + 0.5,
    rotation: Math.random() * 360,
    duration: Math.random() * 20 + 20
}));

export default function SpaceBackground() {
    const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

    useEffect(() => {
        const handleMouseMove = (e) => {
            const x = (e.clientX / window.innerWidth) * 2 - 1;
            const y = (e.clientY / window.innerHeight) * 2 - 1;
            setMousePos({ x, y });
        };
        window.addEventListener("mousemove", handleMouseMove);
        return () => window.removeEventListener("mousemove", handleMouseMove);
    }, []);

    return (
        <Box sx={{ position: "absolute", inset: 0, overflow: "hidden", zIndex: 1 }}>
            <Box sx={{
                position: "absolute", inset: 0,
                background: "radial-gradient(circle at 50% 50%, #171B36 0%, #0B1120 100%)",
            }} />

            <motion.div
                animate={{
                    x: mousePos.x * -30,
                    y: mousePos.y * -30,
                    scale: [1, 1.1, 1],
                    opacity: [0.3, 0.4, 0.3]
                }}
                transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
                style={{
                    position: "absolute",
                    top: "20%", left: "30%",
                    width: "60vw", height: "60vw",
                    background: "radial-gradient(circle, rgba(139,92,246,0.15) 0%, transparent 60%)",
                    filter: "blur(100px)",
                    borderRadius: "50%",
                }}
            />

            <motion.div
                animate={{
                    x: mousePos.x * -20,
                    y: mousePos.y * -20,
                    scale: [1, 1.2, 1],
                    opacity: [0.2, 0.3, 0.2]
                }}
                transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
                style={{
                    position: "absolute",
                    bottom: "10%", right: "10%",
                    width: "70vw", height: "70vw",
                    background: "radial-gradient(circle, rgba(59,130,246,0.1) 0%, transparent 60%)",
                    filter: "blur(120px)",
                    borderRadius: "50%",
                }}
            />

            {STARS.map((star) => (
                <motion.div
                    key={star.id}
                    animate={{
                        opacity: [star.opacity * 0.3, star.opacity, star.opacity * 0.3]
                    }}
                    transition={{
                        duration: star.duration,
                        repeat: Infinity,
                        ease: "easeInOut"
                    }}
                    style={{
                        position: "absolute",
                        left: `${star.x}%`,
                        top: `${star.y}%`,
                        width: star.size,
                        height: star.size,
                        backgroundColor: "#FFF",
                        borderRadius: "50%",
                        boxShadow: `0 0 ${star.size * 2}px rgba(255,255,255,0.8)`
                    }}
                />
            ))}

            {PAPERS.map((paper) => (
                <motion.div
                    key={paper.id}
                    animate={{
                        y: [0, -50, 0],
                        rotate: [paper.rotation, paper.rotation + 45, paper.rotation],
                        x: mousePos.x * -50 * paper.scale
                    }}
                    transition={{
                        duration: paper.duration,
                        repeat: Infinity,
                        ease: "easeInOut"
                    }}
                    style={{
                        position: "absolute",
                        left: `${paper.x}%`,
                        top: `${paper.y}%`,
                        opacity: 0.1,
                        transform: `scale(${paper.scale})`
                    }}
                >
                    <FileText size={100} color="#8B5CF6" strokeWidth={1} />
                </motion.div>
            ))}
        </Box>
    );
}
