import { Box, Typography, Paper, Chip, Collapse } from "@mui/material";
import { motion, AnimatePresence } from "framer-motion";
import { Layers, FileText, ChevronRight, Hash, EyeOff, AlignLeft } from "lucide-react";
import { useState } from "react";

export default function SourcePanel({ sources = [], chatConfig = {}, papers = [] }) {
    const [expandedIndex, setExpandedIndex] = useState(null);

    const toggleExpand = (idx) => {
        setExpandedIndex(expandedIndex === idx ? null : idx);
    };

    const activePaperId = chatConfig.mode === "single" ? chatConfig.paperA : null;
    const activePaper = activePaperId ? papers.find(p => p.paper_id === activePaperId) : null;

    return (
        <Box
            sx={{
                bgcolor: "transparent",
                height: "100%",
                display: "flex",
                flexDirection: "column",
                p: { xs: 2, lg: 3 },
                overflowY: "auto",
                "&::-webkit-scrollbar": { display: "none" },
                scrollbarWidth: "none",
            }}
        >
            <Typography
                variant="subtitle2"
                sx={{
                    color: "#94A3B8",
                    fontWeight: 600,
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    mb: 3,
                    display: "flex",
                    alignItems: "center",
                    gap: 1.5
                }}
            >
                <Layers size={16} />
                Knowledge Context
            </Typography>

            {activePaper ? (
                <Paper
                    sx={{
                        bgcolor: "rgba(255, 255, 255, 0.02)",
                        border: "1px solid rgba(139,92,246,0.3)",
                        borderRadius: "16px",
                        p: 3,
                        mb: 4,
                        display: "flex",
                        flexDirection: "column",
                        gap: 1.5
                    }}
                >
                    <Typography sx={{ color: "#F8FAFC", fontWeight: 700, fontSize: "1rem", lineHeight: 1.3 }}>
                        {activePaper.title}
                    </Typography>
                    {activePaper.authors && (
                        <Typography sx={{ color: "#94A3B8", fontSize: "0.85rem" }}>
                            {activePaper.authors.join(", ")}
                        </Typography>
                    )}
                    <Box sx={{ display: "flex", gap: 2, mt: 1, flexWrap: "wrap" }}>
                        <Box>
                            <Typography variant="caption" sx={{ color: "#64748B", display: "block" }}>Pages</Typography>
                            <Typography variant="body2" sx={{ color: "#E2E8F0", fontWeight: 600 }}>{activePaper.pages || "?"}</Typography>
                        </Box>
                        <Box>
                            <Typography variant="caption" sx={{ color: "#64748B", display: "block" }}>Sections</Typography>
                            <Typography variant="body2" sx={{ color: "#E2E8F0", fontWeight: 600 }}>{activePaper.num_sections || "?"}</Typography>
                        </Box>
                        <Box>
                            <Typography variant="caption" sx={{ color: "#64748B", display: "block" }}>Figures</Typography>
                            <Typography variant="body2" sx={{ color: "#E2E8F0", fontWeight: 600 }}>{activePaper.num_figures || "?"}</Typography>
                        </Box>
                    </Box>
                    <Box sx={{ mt: 1 }}>
                        <Typography variant="caption" sx={{ color: "#64748B", display: "block", mb: 0.5 }}>Keywords</Typography>
                        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
                            {(activePaper.keywords || []).slice(0, 5).map((kw, i) => (
                                <Chip key={i} label={kw} size="small" sx={{ bgcolor: "rgba(139,92,246,0.1)", color: "#A78BFA", height: 20, fontSize: "0.7rem" }} />
                            ))}
                        </Box>
                    </Box>
                </Paper>
            ) : (
                <Paper
                    sx={{
                        bgcolor: "rgba(255, 255, 255, 0.02)",
                        border: "1px dashed rgba(255,255,255,0.1)",
                        borderRadius: "16px",
                        p: 3,
                        mb: 4,
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center",
                        textAlign: "center",
                        minHeight: 180,
                        gap: 1.5
                    }}
                >
                    <EyeOff size={32} color="#475569" />
                    <Typography sx={{ color: "#64748B", fontSize: "0.9rem", fontWeight: 500 }}>
                        PDF Preview Not Available
                    </Typography>
                    <Typography sx={{ color: "#475569", fontSize: "0.8rem", maxWidth: "80%" }}>
                        Select a single paper to view its metadata here.
                    </Typography>
                </Paper>
            )}

            <Typography
                variant="subtitle2"
                sx={{
                    color: "#F8FAFC",
                    fontWeight: 600,
                    mb: 2,
                    display: "flex",
                    alignItems: "center",
                    gap: 1
                }}
            >
                Retrieved Sources
                <Chip label={sources.length} size="small" sx={{ ml: 1, bgcolor: "rgba(255,255,255,0.1)", height: 20 }} />
            </Typography>

            {sources.length === 0 ? (
                <Paper
                    elevation={0}
                    sx={{
                        background: "rgba(255, 255, 255, 0.03)",
                        border: "1px solid rgba(255, 255, 255, 0.05)",
                        color: "#E2E8F0",
                        p: 4,
                        borderRadius: "16px",
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        textAlign: "center",
                        gap: 1
                    }}
                >
                    <FileText size={24} color="#64748B" style={{ marginBottom: 8 }} />
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, color: "#F8FAFC", letterSpacing: "-0.01em" }}>
                        No sources yet
                    </Typography>
                    <Typography variant="body2" sx={{ color: "#94A3B8", lineHeight: 1.6 }}>
                        Ask a question to see retrieved sections and pages dynamically populate here.
                    </Typography>
                </Paper>
            ) : (
                <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                    <AnimatePresence>
                        {sources.map((source, idx) => (
                            <Paper
                                key={idx}
                                component={motion.div}
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ duration: 0.3, delay: idx * 0.1 }}
                                whileHover={{ scale: expandedIndex === idx ? 1 : 1.02 }}
                                onClick={() => toggleExpand(idx)}
                                sx={{
                                    p: 2,
                                    borderRadius: "16px",
                                    bgcolor: expandedIndex === idx ? "rgba(139,92,246,0.1)" : "#1E293B",
                                    border: expandedIndex === idx ? "1px solid rgba(139,92,246,0.5)" : "1px solid rgba(255,255,255,0.05)",
                                    cursor: "pointer",
                                    transition: "all 0.2s",
                                    "&:hover": { borderColor: "rgba(139,92,246,0.3)" }
                                }}
                            >
                                <Typography sx={{ color: "#F8FAFC", fontWeight: 600, fontSize: "0.95rem", mb: 1.5, display: "flex", alignItems: "center", gap: 1 }}>
                                    {source.paper_title || "Unknown Paper"}
                                    <ChevronRight 
                                        size={14} 
                                        color="#64748B" 
                                        style={{ 
                                            transform: expandedIndex === idx ? "rotate(90deg)" : "rotate(0deg)", 
                                            transition: "transform 0.2s" 
                                        }} 
                                    />
                                </Typography>

                                <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mb: 1.5 }}>
                                    {source.section_title && (
                                        <Chip 
                                            icon={<Hash size={12} />} 
                                            label={source.section_title} 
                                            size="small" 
                                            sx={{ bgcolor: "rgba(255,255,255,0.05)", color: "#94A3B8", "& .MuiChip-icon": { color: "#64748B" } }} 
                                        />
                                    )}
                                {(() => {
                                    const pageNum = source.page !== undefined ? source.page : source.page_start;
                                    return pageNum !== undefined && pageNum !== null ? (
                                        <Chip 
                                            label={`p. ${pageNum}`} 
                                            size="small" 
                                            sx={{ bgcolor: "rgba(255,255,255,0.05)", color: "#94A3B8" }} 
                                        />
                                    ) : null;
                                })()}
                                </Box>

                                <Collapse in={expandedIndex === idx}>
                                    <Box sx={{ mt: 2, mb: 1, p: 1.5, bgcolor: "rgba(0,0,0,0.2)", borderRadius: "8px" }}>
                                        <Typography variant="body2" sx={{ color: "#E2E8F0", lineHeight: 1.6, display: "flex", gap: 1 }}>
                                            <AlignLeft size={16} color="#8B5CF6" style={{ minWidth: 16, marginTop: 2 }} />
                                            {source.text || source.chunk_text || "No preview text available."}
                                        </Typography>
                                    </Box>
                                </Collapse>

                                <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mt: expandedIndex === idx ? 1 : 2, pt: 1.5, borderTop: "1px dashed rgba(255,255,255,0.05)" }}>
                                    <Typography variant="caption" sx={{ color: "#64748B" }}>
                                        Relevance Score
                                    </Typography>
                                    <Typography variant="caption" sx={{ color: "#22C55E", fontWeight: 700 }}>
                                        {(source.score * 100).toFixed(1)}%
                                    </Typography>
                                </Box>
                            </Paper>
                        ))}
                    </AnimatePresence>
                </Box>
            )}
        </Box>
    );
}