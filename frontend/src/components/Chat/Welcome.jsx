import { Box, Typography, Grid, Paper } from "@mui/material";
import { motion } from "framer-motion";
import { Sparkles, MessageSquare } from "lucide-react";

export default function Welcome({ onSelect, mode = "collection" }) {
    
    const getSuggestions = () => {
        if (mode === "single") {
            return [
                "Summarize the key findings of this paper",
                "Explain the methodology in simple terms",
                "What datasets were used in this research?",
                "What are the limitations mentioned by the authors?"
            ];
        } else if (mode === "compare") {
            return [
                "Compare the methodologies of these papers",
                "Which paper achieved better results and why?",
                "Compare the datasets used in these papers",
                "What are the different approaches to the problem?"
            ];
        } else {
            return [
                "Which papers use ImageNet?",
                "What is federated learning?",
                "List all paper titles in the registry.",
                "Summarize my research collection."
            ];
        }
    };

    const suggestions = getSuggestions();

    return (
        <Box
            component={motion.div}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            sx={{
                flex: 1,
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                color: "#F8FAFC",
                p: 4,
                textAlign: "center"
            }}
        >
            <motion.div
                animate={{ rotate: [0, 5, -5, 0] }}
                transition={{ repeat: Infinity, duration: 6, ease: "easeInOut" }}
            >
                <Box sx={{
                    width: 80,
                    height: 80,
                    borderRadius: "24px",
                    background: "linear-gradient(135deg, rgba(139,92,246,0.2) 0%, rgba(59,130,246,0.2) 100%)",
                    border: "1px solid rgba(139,92,246,0.3)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    mb: 4,
                    boxShadow: "0 0 40px rgba(139,92,246,0.2)"
                }}>
                    <Sparkles size={40} color="#A78BFA" strokeWidth={2} />
                </Box>
            </motion.div>

            <Typography variant="h3" sx={{ fontWeight: 800, letterSpacing: "-0.03em", mb: 2 }}>
                What would you like to know?
            </Typography>

            <Typography sx={{ color: "#94A3B8", fontSize: "1.1rem", maxWidth: 600, mb: 6, lineHeight: 1.6 }}>
                {mode === "single" && "Ask questions about the selected paper."}
                {mode === "compare" && "Compare the contents, methodology, and results of the selected papers."}
                {mode === "collection" && "Search and discover insights across your entire indexed research library."}
            </Typography>

            <Grid container spacing={3} sx={{ maxWidth: 800 }}>
                {suggestions.map((s, i) => (
                    <Grid item xs={12} sm={6} key={i}>
                        <Paper
                            component={motion.div}
                            whileHover={{ scale: 1.03, y: -4 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => onSelect(s)}
                            sx={{
                                p: 3,
                                bgcolor: "rgba(255,255,255,0.03)",
                                cursor: "pointer",
                                border: "1px solid rgba(255,255,255,0.05)",
                                borderRadius: "20px",
                                display: "flex",
                                flexDirection: "column",
                                alignItems: "flex-start",
                                gap: 2,
                                height: "100%",
                                "&:hover": {
                                    bgcolor: "rgba(255,255,255,0.06)",
                                    borderColor: "rgba(255,255,255,0.1)",
                                    boxShadow: "0 10px 30px -10px rgba(0,0,0,0.3)"
                                }
                            }}
                        >
                            <Box sx={{ p: 1, borderRadius: 2, bgcolor: "rgba(255,255,255,0.05)" }}>
                                <MessageSquare size={20} color="#94A3B8" />
                            </Box>
                            <Typography sx={{ color: "#E2E8F0", fontWeight: 500, textAlign: "left", lineHeight: 1.5 }}>
                                {s}
                            </Typography>
                        </Paper>
                    </Grid>
                ))}
            </Grid>
        </Box>
    );
}