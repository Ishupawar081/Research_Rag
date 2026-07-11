import { Box, Paper, Typography, Avatar, IconButton, Tooltip } from "@mui/material";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import { Copy, RefreshCw, CheckCircle2, ThumbsUp, ThumbsDown } from "lucide-react";
import { useState } from "react";
import { motion } from "framer-motion";
import { useTheme } from "@mui/material/styles";
import { useAuth } from "../../contexts/AuthContext";

export default function ChatMessage({ role, text, timestamp }) {
    const { user } = useAuth();
    const theme = useTheme();
    const isUser = role === "user";
    const [copied, setCopied] = useState(false);
    const [feedback, setFeedback] = useState(null);

    const handleCopy = () => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <Box
            component={motion.div}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            sx={{
                display: "flex",
                flexDirection: isUser ? "row-reverse" : "row",
                gap: 2,
                mb: 3,
                maxWidth: "100%",
                px: { xs: 1, md: 2 }
            }}
        >
            <Avatar 
                src={isUser ? user?.user_metadata?.avatar_url : null}
                sx={{ 
                    width: 36, 
                    height: 36, 
                    bgcolor: isUser ? "transparent" : (theme.palette.mode === 'dark' ? "rgba(139,92,246,0.2)" : "rgba(139,92,246,0.1)"),
                    color: theme.palette.primary.main,
                    border: isUser ? "none" : `1px solid ${theme.palette.divider}`
                }}
            >
                {!isUser && "AI"}
            </Avatar>

            <Box sx={{ display: "flex", flexDirection: "column", maxWidth: "80%", alignItems: isUser ? "flex-end" : "flex-start" }}>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 0.5 }}>
                    <Typography variant="caption" sx={{ fontWeight: 600, color: "text.secondary" }}>
                        {isUser ? "You" : "Assistant"}
                    </Typography>
                    {timestamp && (
                        <Typography variant="caption" sx={{ color: theme.palette.mode === 'dark' ? "#475569" : "#94A3B8" }}>
                            • {timestamp}
                        </Typography>
                    )}
                </Box>

                <Paper
                    elevation={0}
                    sx={{
                        p: 2.5,
                        borderRadius: "20px",
                        borderTopRightRadius: isUser ? "4px" : "20px",
                        borderTopLeftRadius: !isUser ? "4px" : "20px",
                        bgcolor: isUser ? "transparent" : "background.paper",
                        background: isUser ? "linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)" : "none",
                        color: isUser ? "#F8FAFC" : "text.primary",
                        border: isUser ? "none" : `1px solid ${theme.palette.divider}`,
                        boxShadow: isUser ? "0 8px 24px -6px rgba(59, 130, 246, 0.4)" : (theme.palette.mode === 'dark' ? "0 4px 20px rgba(0,0,0,0.15)" : "0 4px 20px rgba(0,0,0,0.05)"),
                        overflowX: "auto",
                        "& p": { m: 0, "& + p": { mt: 1.5 } },
                        "& pre": { bgcolor: "rgba(0,0,0,0.3)", p: 1.5, borderRadius: 2, overflowX: "auto", mt: 1.5, mb: 1.5 },
                        "& code": { fontFamily: "monospace", bgcolor: "rgba(0,0,0,0.2)", px: 0.5, borderRadius: 1 },
                        "& table": { borderCollapse: "collapse", width: "100%", mt: 2, mb: 2 },
                        "& th, & td": { border: "1px solid rgba(255,255,255,0.1)", p: 1 },
                        "& th": { bgcolor: "rgba(255,255,255,0.05)" },
                        "& ul, & ol": { mt: 1, mb: 1, pl: 3 },
                        "& li": { mb: 0.5 },
                        "& a": { color: "#60A5FA", textDecoration: "none", "&:hover": { textDecoration: "underline" } },
                    }}
                >
                    <ReactMarkdown 
                        remarkPlugins={[remarkGfm, remarkMath]}
                        rehypePlugins={[rehypeKatex]}
                    >
                        {text}
                    </ReactMarkdown>
                </Paper>

                {!isUser && (
                    <Box sx={{ display: "flex", gap: 1, mt: 1 }}>
                        <Tooltip title="Copy Answer">
                            <IconButton size="small" onClick={handleCopy} sx={{ color: "text.secondary", "&:hover": { color: "text.primary" } }}>
                                {copied ? <CheckCircle2 size={16} color={theme.palette.success.main} /> : <Copy size={16} />}
                            </IconButton>
                        </Tooltip>
                        
                        <Tooltip title="Regenerate">
                            <IconButton size="small" sx={{ color: "text.secondary", "&:hover": { color: "text.primary" } }}>
                                <RefreshCw size={16} />
                            </IconButton>
                        </Tooltip>
                        <Tooltip title="Helpful">
                            <IconButton size="small" onClick={() => setFeedback("like")} sx={{ color: feedback === "like" ? theme.palette.success.main : "text.secondary", "&:hover": { color: theme.palette.success.main } }}>
                                <ThumbsUp size={16} />
                            </IconButton>
                        </Tooltip>
                        <Tooltip title="Dislike">
                            <IconButton size="small" onClick={() => setFeedback("dislike")} sx={{ color: feedback === "dislike" ? theme.palette.error?.main || "#FCA5A5" : "text.secondary", "&:hover": { color: theme.palette.error?.main || "#FCA5A5" } }}>
                                <ThumbsDown size={16} />
                            </IconButton>
                        </Tooltip>
                    </Box>
                )}
            </Box>
        </Box>
    );
}