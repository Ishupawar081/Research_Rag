import { Box, Typography } from "@mui/material";
import { motion } from "framer-motion";
import { useState, useEffect } from "react";

const dotVariants = {
    initial: { y: 0, opacity: 0.5 },
    animate: { y: -6, opacity: 1 }
};

const LOADING_STEPS = [
    "Thinking...",
    "Retrieving relevant papers...",
    "Searching embeddings...",
    "Analyzing context...",
    "Generating answer..."
];

export default function TypingIndicator() {
    const [stepIndex, setStepIndex] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setStepIndex(prev => (prev + 1) % LOADING_STEPS.length);
        }, 2000);
        return () => clearInterval(interval);
    }, []);

    return (
        <Box sx={{ display: "flex", justifyContent: "flex-start", mt: 2, mb: 2 }}>
            <Box sx={{
                bgcolor: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.05)",
                p: 2,
                px: 3,
                borderRadius: "20px",
                display: "flex",
                gap: 2,
                alignItems: "center"
            }}>
                <Box sx={{ display: "flex", gap: 0.8, alignItems: "center", pt: 1 }}>
                    {[0, 1, 2].map((index) => (
                        <motion.div
                            key={index}
                            variants={dotVariants}
                            initial="initial"
                            animate="animate"
                            transition={{
                                duration: 0.5,
                                repeat: Infinity,
                                repeatType: "reverse",
                                delay: index * 0.15,
                                ease: "easeInOut"
                            }}
                            style={{
                                width: 6,
                                height: 6,
                                backgroundColor: "#8B5CF6",
                                borderRadius: "50%",
                                boxShadow: "0 0 10px rgba(139,92,246,0.5)"
                            }}
                        />
                    ))}
                </Box>
                <Typography variant="body2" sx={{ color: "#94A3B8", fontStyle: "italic", fontWeight: 500 }}>
                    {LOADING_STEPS[stepIndex]}
                </Typography>
            </Box>
        </Box>
    );
}