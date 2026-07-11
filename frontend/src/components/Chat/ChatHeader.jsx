import { Box, Typography, Chip, IconButton, Tooltip } from "@mui/material";
import { Sparkles, RefreshCw, Trash2 } from "lucide-react";

export default function ChatHeader({ mode = "Collection", paper = null, paper2 = null, onNewChat, onClear }) {
    return (
        <Box
            sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                px: 4,
                py: 2.5,
                borderBottom: "1px solid rgba(255,255,255,0.05)",
                bgcolor: "rgba(255,255,255,0.01)"
            }}
        >
            <Box>
                <Typography variant="h6" sx={{ color: "#F8FAFC", fontWeight: 700, letterSpacing: "-0.01em" }}>
                    AI Research Assistant
                </Typography>
                <Typography variant="body2" sx={{ color: "#64748B", mt: 0.2 }}>
                    Current Session
                </Typography>
            </Box>

            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                <Chip
                    icon={<Sparkles size={14} color="#A78BFA" />}
                    label={mode}
                    sx={{
                        bgcolor: "rgba(139, 92, 246, 0.15)",
                        color: "#A78BFA",
                        border: "1px solid rgba(139, 92, 246, 0.3)",
                        fontWeight: 600,
                        "& .MuiChip-icon": { ml: 1 }
                    }}
                />

                {paper && (
                    <Chip
                        label={paper}
                        variant="outlined"
                        sx={{ borderColor: "rgba(255,255,255,0.1)", color: "#94A3B8" }}
                    />
                )}

                {paper2 && (
                    <Typography variant="body2" sx={{ color: "#64748B", px: 0.5 }}>
                        vs
                    </Typography>
                )}

                {paper2 && (
                    <Chip
                        label={paper2}
                        variant="outlined"
                        sx={{ borderColor: "rgba(255,255,255,0.1)", color: "#94A3B8" }}
                    />
                )}

                <Box sx={{ display: "flex", gap: 1, ml: 2 }}>
                    <Tooltip title="Export Chat">
                        <IconButton onClick={() => window.dispatchEvent(new CustomEvent('export-chat'))} sx={{ color: "#64748B", "&:hover": { color: "#F8FAFC", bgcolor: "rgba(255,255,255,0.05)" } }}>
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
                        </IconButton>
                    </Tooltip>

                    <Tooltip title="New Chat">
                        <IconButton onClick={onNewChat} sx={{ color: "#64748B", "&:hover": { color: "#F8FAFC", bgcolor: "rgba(255,255,255,0.05)" } }}>
                            <RefreshCw size={18} />
                        </IconButton>
                    </Tooltip>

                    <Tooltip title="Clear Conversation">
                        <IconButton onClick={onClear} sx={{ color: "#64748B", "&:hover": { color: "#EF4444", bgcolor: "rgba(239,68,68,0.1)" } }}>
                            <Trash2 size={18} />
                        </IconButton>
                    </Tooltip>
                </Box>
            </Box>
        </Box>
    );
}