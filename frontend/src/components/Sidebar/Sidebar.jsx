import { useState, useEffect } from "react";
import {
    Box,
    Typography,
    Button,
    Divider,
    Paper,
    Chip,
    InputBase,
    Tooltip
} from "@mui/material";

import { motion } from "framer-motion";
import { 
    Plus, 
    FileText, 
    Library, 
    GitCompare, 
    UploadCloud, 
    History, 
    Database,
    Zap,
    Search
} from "lucide-react";

import { useTheme } from "@mui/material/styles";

import UploadOverlay from "../Upload/UploadOverlay";
import PaperSelector from "../Paper/PaperSelector";
import CompareSelector from "../Paper/CompareSelector";

export default function Sidebar({ 
    indexedCount, 
    onUploadComplete, 
    chatHistory = [], 
    onSelectChat,
    onNewChat,
    activeChatId,
    papers = [], 
    registryStatus,
    chatConfig,
    setChatConfig,
    globalSearchQuery = "",
    modelInfo = { llm: "Unknown", embedding: "Unknown" }
}) {
    const theme = useTheme();
    const [uploadOpen, setUploadOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");

    useEffect(() => {
        const handleOpenUpload = () => setUploadOpen(true);
        window.addEventListener('open-upload', handleOpenUpload);
        return () => window.removeEventListener('open-upload', handleOpenUpload);
    }, []);

    const effectiveSearch = searchQuery || globalSearchQuery;

    const filteredPapers = papers.filter(p => {
        const searchTarget = (
            p.title + 
            " " + (p.authors ? p.authors.join(" ") : "") + 
            " " + (p.keywords ? p.keywords.join(" ") : "") +
            " " + (p.paper_id || "")
        ).toLowerCase();
        
        return searchTarget.includes(effectiveSearch.toLowerCase());
    });

    const handleModeChange = (mode) => {
        setChatConfig(prev => ({ ...prev, mode }));
    };

    return (
        <Box
            sx={{
                bgcolor: "transparent",
                color: "text.primary",
                p: 3,
                height: "100%",
                display: "flex",
                flexDirection: "column",
                overflowY: "auto",
                "&::-webkit-scrollbar": { display: "none" },
                scrollbarWidth: "none",
            }}
        >
            {/* Workspace Header */}
            <Typography
                variant="subtitle2"
                sx={{
                    color: "text.secondary",
                    fontWeight: 600,
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    mb: 2
                }}
            >
                Workspace
            </Typography>

            <Button
                variant="contained"
                startIcon={<Plus size={18} />}
                fullWidth
                sx={{ mb: 3 }}
                onClick={() => onNewChat()}
            >
                New Chat
            </Button>

            <Box sx={{ 
                display: "flex", 
                alignItems: "center", 
                bgcolor: "rgba(255,255,255,0.05)", 
                borderRadius: "12px", 
                px: 2, 
                py: 1, 
                mb: 3 
            }}>
                <Search size={18} color="#64748B" style={{ marginRight: 8 }} />
                <InputBase
                    placeholder="Search registry..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    sx={{ color: "#F8FAFC", fontSize: "0.9rem", flex: 1 }}
                />
            </Box>

            <Typography
                variant="subtitle2"
                sx={{
                    color: "#94A3B8",
                    fontWeight: 600,
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    mb: 2
                }}
            >
                Chat Modes
            </Typography>

            <Box sx={{ display: "flex", flexDirection: "column", gap: 1, mb: 1 }}>
                <Button
                    variant="outlined"
                    startIcon={<FileText size={18} />}
                    fullWidth
                    onClick={() => handleModeChange("single")}
                    sx={{
                        justifyContent: "flex-start",
                        bgcolor: chatConfig.mode === "single" ? "rgba(139, 92, 246, 0.1)" : "transparent",
                        borderColor: chatConfig.mode === "single" ? "rgba(139, 92, 246, 0.3)" : "transparent",
                        color: chatConfig.mode === "single" ? "#A78BFA" : "#F8FAFC",
                        "&:hover": { bgcolor: "rgba(139, 92, 246, 0.15)" },
                        border: chatConfig.mode === "single" ? undefined : "none"
                    }}
                >
                    Single Paper
                </Button>
                <Button
                    variant="outlined"
                    startIcon={<Library size={18} />}
                    fullWidth
                    onClick={() => handleModeChange("collection")}
                    sx={{ 
                        justifyContent: "flex-start", 
                        bgcolor: chatConfig.mode === "collection" ? "rgba(59, 130, 246, 0.1)" : "transparent",
                        borderColor: chatConfig.mode === "collection" ? "rgba(59, 130, 246, 0.3)" : "transparent",
                        color: chatConfig.mode === "collection" ? "#93C5FD" : "#F8FAFC",
                        "&:hover": { bgcolor: "rgba(59, 130, 246, 0.15)" },
                        border: chatConfig.mode === "collection" ? undefined : "none"
                    }}
                >
                    Collection
                </Button>
                <Button
                    variant="outlined"
                    startIcon={<GitCompare size={18} />}
                    fullWidth
                    onClick={() => handleModeChange("compare")}
                    sx={{ 
                        justifyContent: "flex-start", 
                        bgcolor: chatConfig.mode === "compare" ? "rgba(16, 185, 129, 0.1)" : "transparent",
                        borderColor: chatConfig.mode === "compare" ? "rgba(16, 185, 129, 0.3)" : "transparent",
                        color: chatConfig.mode === "compare" ? "#6EE7B7" : "#F8FAFC",
                        "&:hover": { bgcolor: "rgba(16, 185, 129, 0.15)" },
                        border: chatConfig.mode === "compare" ? undefined : "none"
                    }}
                >
                    Compare Papers
                </Button>
            </Box>

            <Box sx={{ mb: 3 }}>
                {chatConfig.mode === "single" && (
                    <PaperSelector 
                        papers={filteredPapers} 
                        selectedPaperId={chatConfig.paperA} 
                        onChange={(id) => setChatConfig(prev => ({ ...prev, paperA: id }))} 
                    />
                )}
                {chatConfig.mode === "compare" && (
                    <CompareSelector 
                        papers={filteredPapers} 
                        paperA={chatConfig.paperA} 
                        paperB={chatConfig.paperB} 
                        onChange={(a, b) => setChatConfig(prev => ({ ...prev, paperA: a, paperB: b }))} 
                    />
                )}
            </Box>

            <Button
                variant="outlined"
                startIcon={<UploadCloud size={18} />}
                fullWidth
                onClick={() => setUploadOpen(true)}
                sx={{
                    justifyContent: "center",
                    borderStyle: "dashed",
                    borderColor: "rgba(255,255,255,0.2)",
                    mb: 3,
                    py: 1.5,
                }}
            >
                Upload PDF
            </Button>

            <Divider sx={{ mb: 3 }} />

            {/* Recent Chats */}
            <Typography
                variant="subtitle2"
                sx={{
                    color: "#94A3B8",
                    fontWeight: 600,
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    mb: 2
                }}
            >
                Recent Conversations
            </Typography>

            <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5, mb: 4 }}>
                {chatHistory.length === 0 && (
                    <Typography variant="body2" sx={{ color: "#64748B", fontStyle: "italic", px: 1 }}>
                        No recent conversations
                    </Typography>
                )}
                {chatHistory.slice(0, 10).map((chat) => (
                    <Paper
                        key={chat.id}
                        component={motion.div}
                        whileHover={{ scale: 1.02 }}
                        onClick={() => onSelectChat(chat)}
                        sx={{
                            p: 2,
                            bgcolor: activeChatId === chat.id ? "rgba(139,92,246,0.15)" : "rgba(255,255,255,0.02)",
                            border: activeChatId === chat.id ? "1px solid rgba(139,92,246,0.4)" : "1px solid transparent",
                            cursor: "pointer",
                            transition: "background 0.2s",
                            position: "relative",
                            "&:hover": { 
                                bgcolor: activeChatId === chat.id ? "rgba(139,92,246,0.2)" : "rgba(255,255,255,0.05)",
                                "& .chat-actions": { opacity: 1 }
                            }
                        }}
                    >
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 0.5 }}>
                            <History size={16} color={activeChatId === chat.id ? "#A78BFA" : "#64748B"} />
                            <Typography sx={{ fontWeight: 500, fontSize: "0.9rem", color: activeChatId === chat.id ? "#F8FAFC" : "#E2E8F0", width: "160px" }} noWrap>
                                {chat.title}
                            </Typography>
                        </Box>
                        <Typography variant="caption" sx={{ color: "#64748B", ml: 3.5 }}>
                            {chat.time || new Date(chat.date).toLocaleDateString()}
                        </Typography>
                        <Box className="chat-actions" sx={{ 
                            position: "absolute", right: 8, top: "50%", transform: "translateY(-50%)", 
                            opacity: 0, transition: "opacity 0.2s", display: "flex", gap: 0.5 
                        }}>
                            <Tooltip title="Rename coming soon">
                                <span>
                                    <Button 
                                        disabled
                                        size="small" 
                                        sx={{ minWidth: 0, p: 0.5, color: "#94A3B8" }}
                                        onClick={(e) => { e.stopPropagation(); }}
                                    >
                                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>
                                    </Button>
                                </span>
                            </Tooltip>
                            <Tooltip title="Delete coming soon">
                                <span>
                                    <Button 
                                        disabled
                                        size="small" 
                                        sx={{ minWidth: 0, p: 0.5, color: "#64748B" }}
                                        onClick={(e) => { e.stopPropagation(); }}
                                    >
                                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                                    </Button>
                                </span>
                            </Tooltip>
                        </Box>
                    </Paper>
                ))}
            </Box>

            <Box sx={{ flexGrow: 1 }} />

            {/* Stats */}
            <Paper
                sx={{
                    p: 2.5,
                    bgcolor: registryStatus === "error" ? "rgba(239, 68, 68, 0.05)" : "rgba(59, 130, 246, 0.05)",
                    border: "1px solid",
                    borderColor: registryStatus === "error" ? "rgba(239, 68, 68, 0.15)" : "rgba(59, 130, 246, 0.15)",
                }}
            >
                <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 2 }}>
                    <Database size={18} color={registryStatus === "error" ? "#EF4444" : "#3B82F6"} />
                    <Typography sx={{ fontWeight: 600, color: registryStatus === "error" ? "#FCA5A5" : "#93C5FD", fontSize: "0.9rem" }}>
                        Knowledge Base
                    </Typography>
                </Box>
                <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 1.5 }}>
                    <Typography variant="body2" color="#94A3B8">Indexed Papers</Typography>
                    {registryStatus === "loading" ? (
                        <Typography variant="caption" sx={{ color: "#94A3B8" }}>Loading...</Typography>
                    ) : registryStatus === "error" ? (
                        <Typography variant="caption" sx={{ color: "#EF4444" }}>Offline</Typography>
                    ) : (
                        <Chip label={indexedCount !== undefined ? indexedCount : "-"} size="small" sx={{ bgcolor: "rgba(255,255,255,0.1)", color: "#F8FAFC" }} />
                    )}
                </Box>
                <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 1.5 }}>
                    <Typography variant="body2" color="#94A3B8">Total Chunks</Typography>
                    <Chip label={papers.reduce((sum, p) => sum + (p.num_chunks || 0), 0)} size="small" sx={{ bgcolor: "rgba(255,255,255,0.1)", color: "#F8FAFC" }} />
                </Box>
                <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 1.5 }}>
                    <Typography variant="body2" color="#94A3B8">Current LLM</Typography>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                        <Zap size={14} color="#F59E0B" />
                        <Typography variant="caption" sx={{ fontWeight: 600, color: "#E2E8F0" }}>{modelInfo.llm}</Typography>
                    </Box>
                </Box>
                <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <Typography variant="body2" color="#94A3B8">Embedding</Typography>
                    <Typography variant="caption" sx={{ fontWeight: 600, color: "#E2E8F0" }}>{modelInfo.embedding}</Typography>
                </Box>
            </Paper>

            <UploadOverlay 
                open={uploadOpen} 
                onClose={() => setUploadOpen(false)} 
                onComplete={onUploadComplete} 
            />

        </Box>
    );
}