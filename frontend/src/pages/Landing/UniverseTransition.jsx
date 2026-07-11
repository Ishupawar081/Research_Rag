import { Box } from "@mui/material";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { FileText } from "lucide-react";

// Generate these outside the component to satisfy ESLint react-hooks/purity rules
const PARTICLES = Array.from({ length: 150 }).map((_, i) => ({
    id: i,
    angle: Math.random() * Math.PI * 2,
    distance: Math.random() * 1500 + 200,
    size: Math.random() * 4 + 1,
    color: Math.random() > 0.5 ? "#8B5CF6" : "#3B82F6",
    duration: 2 + Math.random()
}));

const FLYING_PAPERS = Array.from({ length: 20 }).map((_, i) => ({
    id: i,
    angle: Math.random() * Math.PI * 2,
    distance: Math.random() * 1000 + 300,
    rotation: Math.random() * 720 - 360,
    scale: Math.random() * 1.5 + 0.5,
    duration: 2.5 + Math.random()
}));

export default function UniverseTransition({ onComplete }) {
    const [phase, setPhase] = useState("darkness");

    useEffect(() => {
        const t1 = setTimeout(() => setPhase("singularity"), 800);
        const t2 = setTimeout(() => setPhase("explosion"), 1000);
        const t3 = setTimeout(() => setPhase("portal"), 2800);
        const t4 = setTimeout(() => setPhase("engulf"), 3500);
        const t5 = setTimeout(() => {
            if (onComplete) onComplete();
        }, 4000);

        return () => {
            clearTimeout(t1);
            clearTimeout(t2);
            clearTimeout(t3);
            clearTimeout(t4);
            clearTimeout(t5);
        };
    }, [onComplete]);

    return (
        <Box sx={{
            position: "absolute",
            inset: 0,
            zIndex: 50,
            bgcolor: "#000",
            overflow: "hidden",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            perspective: "1000px"
        }}>
            
            <motion.div
                initial={{ scale: 0, opacity: 0 }}
                animate={{
                    scale: phase === "singularity" ? 1 : phase === "explosion" || phase === "portal" || phase === "engulf" ? 0 : 0,
                    opacity: phase === "singularity" ? 1 : 0
                }}
                transition={{ duration: 0.2 }}
                style={{
                    position: "absolute",
                    width: 4,
                    height: 4,
                    backgroundColor: "#FFF",
                    borderRadius: "50%",
                    boxShadow: "0 0 20px 10px rgba(255,255,255,0.8)"
                }}
            />

            {(phase === "explosion" || phase === "portal" || phase === "engulf") && (
                <>
                    <motion.div
                        initial={{ scale: 0, opacity: 1 }}
                        animate={{ scale: 100, opacity: 0 }}
                        transition={{ duration: 1.5, ease: "easeOut" }}
                        style={{
                            position: "absolute",
                            width: 50,
                            height: 50,
                            backgroundColor: "#FFF",
                            borderRadius: "50%",
                            boxShadow: "0 0 100px 50px rgba(255,255,255,1)"
                        }}
                    />

                    {PARTICLES.map(p => (
                        <motion.div
                            key={`p-${p.id}`}
                            initial={{ x: 0, y: 0, opacity: 1, scale: 0 }}
                            animate={{
                                x: Math.cos(p.angle) * p.distance,
                                y: Math.sin(p.angle) * p.distance,
                                opacity: 0,
                                scale: p.size
                            }}
                            transition={{ duration: p.duration, ease: "easeOut" }}
                            style={{
                                position: "absolute",
                                width: 2,
                                height: 2,
                                backgroundColor: p.color,
                                borderRadius: "50%",
                                boxShadow: `0 0 10px ${p.color}`
                            }}
                        />
                    ))}

                    {FLYING_PAPERS.map(p => (
                        <motion.div
                            key={`doc-${p.id}`}
                            initial={{ x: 0, y: 0, z: -500, rotateZ: 0, opacity: 0 }}
                            animate={{
                                x: Math.cos(p.angle) * p.distance,
                                y: Math.sin(p.angle) * p.distance,
                                z: 500,
                                rotateZ: p.rotation,
                                opacity: [0, 0.8, 0]
                            }}
                            transition={{ duration: p.duration, ease: "easeInOut" }}
                            style={{
                                position: "absolute",
                                color: "rgba(255,255,255,0.1)",
                            }}
                        >
                            <FileText size={40 * p.scale} strokeWidth={1} />
                        </motion.div>
                    ))}
                </>
            )}

            {(phase === "portal" || phase === "engulf") && (
                <motion.div
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ 
                        scale: phase === "engulf" ? 50 : 1, 
                        opacity: 1 
                    }}
                    transition={{ 
                        duration: phase === "engulf" ? 0.8 : 0.7, 
                        ease: "easeInOut" 
                    }}
                    style={{
                        position: "absolute",
                        width: 200,
                        height: 200,
                        borderRadius: "50%",
                        background: "radial-gradient(circle, rgba(255,255,255,1) 0%, rgba(139,92,246,0.8) 40%, rgba(59,130,246,0) 70%)",
                        boxShadow: "0 0 100px 50px rgba(139,92,246,0.5)",
                        filter: "blur(10px)"
                    }}
                />
            )}

            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: phase === "engulf" ? 1 : 0 }}
                transition={{ duration: 0.5 }}
                style={{
                    position: "absolute",
                    inset: 0,
                    backgroundColor: "#0B1120",
                    zIndex: 100
                }}
            />
        </Box>
    );
}
