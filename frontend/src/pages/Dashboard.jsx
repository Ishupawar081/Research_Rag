import { useState, useEffect } from "react";
import { Box, Typography, Button, Container, Grid, Card, CardContent, IconButton, Divider, GlobalStyles, Tooltip } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { FileText, Library, GitCompare, Plus, Clock, FileUp, MoreVertical, LogOut, MessageSquare, Sparkles } from "lucide-react";
import { v4 as uuidv4 } from "uuid";
import { api } from "../api/chat";
import { supabase } from "../lib/supabase";
import { useAuth } from "../contexts/AuthContext";
import { motion } from "framer-motion";
import UserProfileMenu from "../components/Common/UserProfileMenu";
import { useTheme } from "@mui/material/styles";

export default function Dashboard() {
    const navigate = useNavigate();
    const { user } = useAuth();
    const theme = useTheme();
    const [recentChats, setRecentChats] = useState([]);
    const [recentPapers, setRecentPapers] = useState([]);

    useEffect(() => {

        // Fetch chats from Supabase
        if (user) {
            supabase.from('chats')
                .select('*')
                .eq('user_id', user.id)
                .order('created_at', { ascending: false })
                .limit(5)
                .then(({ data, error }) => {
                    if (data) {
                        setRecentChats(data);
                    }
                });
        }

        api.get("/papers")
            .then(res => setRecentPapers(res.data.papers ? res.data.papers.slice(0, 5) : []))
            .catch(err => console.error("Failed to load papers:", err));
    }, []);

    const createNewChat = async (mode) => {
        const chatId = uuidv4();
        const newChat = {
            id: chatId,
            user_id: user.id,
            mode: mode,
            title: `New ${mode.charAt(0).toUpperCase() + mode.slice(1)} Chat`,
            created_at: new Date().toISOString()
        };
        
        await supabase.from('chats').insert([newChat]);
        
        const updatedChats = [newChat, ...recentChats];
        setRecentChats(updatedChats);
        navigate(`/workspace/${chatId}`);
    };

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } }
    };

    return (
        <Box sx={{ minHeight: "100vh", bgcolor: "background.default", color: "text.primary", pb: 10, position: "relative", overflow: "hidden" }}>
            <GlobalStyles styles={{ body: { backgroundColor: theme.palette.background.default } }} />
            
            {/* Ambient Background Glows */}
            <Box sx={{
                position: "absolute", top: "-10%", left: "-5%", width: "40vw", height: "40vw",
                background: "radial-gradient(circle, rgba(139,92,246,0.08) 0%, transparent 60%)",
                filter: "blur(80px)", pointerEvents: "none", zIndex: 0
            }} />
            <Box sx={{
                position: "absolute", bottom: "-10%", right: "-5%", width: "40vw", height: "40vw",
                background: "radial-gradient(circle, rgba(59,130,246,0.08) 0%, transparent 60%)",
                filter: "blur(80px)", pointerEvents: "none", zIndex: 0
            }} />

            {/* Header */}
            <Box sx={{ borderBottom: `1px solid ${theme.palette.divider}`, bgcolor: theme.palette.mode === 'dark' ? "rgba(11,17,32,0.8)" : "rgba(255,255,255,0.8)", position: 'sticky', top: 0, zIndex: 10, backdropFilter: "blur(20px)" }}>
                <Container maxWidth="xl" sx={{ display: 'flex', alignItems: 'center', py: 2 }}>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
                        <Box sx={{ p: 1, borderRadius: 2, background: "linear-gradient(135deg, rgba(139,92,246,0.2) 0%, rgba(59,130,246,0.2) 100%)", border: "1px solid rgba(139,92,246,0.3)" }}>
                            <Sparkles size={20} color={theme.palette.primary.main} />
                        </Box>
                        <Typography variant="h5" sx={{ fontWeight: 800, letterSpacing: "-0.02em", background: theme.palette.mode === 'dark' ? "linear-gradient(to right, #F8FAFC, #A78BFA)" : "linear-gradient(to right, #0F172A, #7C3AED)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
                            Research AI
                        </Typography>
                    </Box>
                    <Box sx={{ ml: 'auto', display: 'flex', alignItems: 'center', gap: 3 }}>
                        <UserProfileMenu />
                    </Box>
                </Container>
            </Box>

            <Container 
                maxWidth="xl" 
                sx={{ mt: 8, position: "relative", zIndex: 1 }}
                component={motion.div}
                variants={containerVariants}
                initial="hidden"
                animate="visible"
            >
                <motion.div variants={itemVariants}>
                    <Typography variant="h3" sx={{ fontWeight: 800, mb: 1, letterSpacing: "-0.02em" }}>Welcome back, {user?.user_metadata?.full_name?.split(' ')[0] || user?.email?.split('@')[0] || "Researcher"}.</Typography>
                    <Typography sx={{ color: "text.secondary", mb: 8, fontSize: "1.1rem" }}>Pick up where you left off or start a new deep dive into the literature.</Typography>
                </motion.div>

                <Grid container spacing={4}>
                    {/* Left Column: Actions & Chats */}
                    <Grid item xs={12} md={8}>
                        <motion.div variants={itemVariants}>
                            <Typography variant="h6" sx={{ fontWeight: 600, mb: 3, display: "flex", alignItems: "center", gap: 1.5 }}>
                                <Plus size={20} color={theme.palette.primary.main} /> Start a New Session
                            </Typography>
                            <Grid container spacing={2.5} sx={{ mb: 8 }}>
                                {[
                                    { mode: "single", icon: <FileText size={28} />, title: "Single Paper", desc: "Chat deeply with a specific document", color: "139,92,246" },
                                    { mode: "collection", icon: <Library size={28} />, title: "Collection Chat", desc: "Search and query across all papers", color: "59,130,246" },
                                    { mode: "compare", icon: <GitCompare size={28} />, title: "Compare Papers", desc: "Analyze multiple publications", color: "16,185,129" }
                                ].map(action => (
                                    <Grid item xs={12} sm={4} key={action.mode}>
                                        <Card 
                                            component={motion.div}
                                            whileHover={{ y: -8, scale: 1.02 }}
                                            onClick={() => createNewChat(action.mode)}
                                            sx={{ 
                                                bgcolor: "background.paper", 
                                                backdropFilter: "blur(20px)",
                                                border: `1px solid ${theme.palette.divider}`, 
                                                borderRadius: 4, color: "text.primary", cursor: "pointer",
                                                boxShadow: "0 10px 40px -10px rgba(0,0,0,0.3)",
                                                position: "relative",
                                                overflow: "hidden",
                                                height: "100%",
                                                "&:hover": { 
                                                    borderColor: `rgba(${action.color},0.5)`,
                                                    boxShadow: `0 20px 40px -10px rgba(${action.color},0.2)`
                                                }
                                            }}
                                        >
                                            <Box sx={{ position: "absolute", top: 0, left: 0, right: 0, height: "2px", background: `linear-gradient(90deg, rgba(${action.color},1) 0%, transparent 100%)`, opacity: 0.5 }} />
                                            <CardContent sx={{ p: 3.5 }}>
                                                <Box sx={{ 
                                                    color: `rgb(${action.color})`, mb: 3, 
                                                    display: "inline-flex", p: 1.5, borderRadius: 3, 
                                                    bgcolor: `rgba(${action.color},0.1)`,
                                                    border: `1px solid rgba(${action.color},0.2)`
                                                }}>
                                                    {action.icon}
                                                </Box>
                                                <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>{action.title}</Typography>
                                                <Typography sx={{ color: "text.secondary", fontSize: "0.9rem", lineHeight: 1.5 }}>{action.desc}</Typography>
                                            </CardContent>
                                        </Card>
                                    </Grid>
                                ))}
                            </Grid>
                        </motion.div>

                        <motion.div variants={itemVariants}>
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                                <Typography variant="h6" sx={{ fontWeight: 600, display: "flex", alignItems: "center", gap: 1.5 }}>
                                    <Clock size={20} color={theme.palette.secondary.main} /> Recent Conversations
                                </Typography>
                            </Box>
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                {recentChats.length === 0 ? (
                                    <Box sx={{ p: 6, textAlign: 'center', bgcolor: theme.palette.mode === 'dark' ? "rgba(255,255,255,0.02)" : "rgba(0,0,0,0.02)", borderRadius: 4, border: `1px dashed ${theme.palette.divider}` }}>
                                        <MessageSquare size={40} color={theme.palette.text.secondary} style={{ marginBottom: 16 }} />
                                        <Typography sx={{ color: "text.primary", fontWeight: 500, mb: 1 }}>No conversations yet</Typography>
                                        <Typography sx={{ color: "text.secondary", fontSize: "0.9rem" }}>Your recent analysis sessions will appear here.</Typography>
                                    </Box>
                                ) : (
                                    recentChats.slice(0, 5).map(chat => (
                                        <Box 
                                            key={chat.id}
                                            component={motion.div}
                                            whileHover={{ scale: 1.01, x: 5 }}
                                            onClick={() => navigate(`/workspace/${chat.id}`)}
                                            sx={{ 
                                                p: 2.5, bgcolor: "background.paper", borderRadius: 3, 
                                                border: `1px solid ${theme.palette.divider}`, display: 'flex', alignItems: 'center', cursor: 'pointer',
                                                backdropFilter: "blur(10px)",
                                                transition: "background 0.2s, border-color 0.2s",
                                                "&:hover": { bgcolor: theme.palette.action.hover, borderColor: theme.palette.primary.main }
                                            }}
                                        >
                                            <Box sx={{ 
                                                p: 1.5, borderRadius: 2, mr: 2.5,
                                                bgcolor: chat.mode === 'single' ? 'rgba(139,92,246,0.1)' : chat.mode === 'collection' ? 'rgba(59,130,246,0.1)' : 'rgba(16,185,129,0.1)',
                                                color: chat.mode === 'single' ? '#A78BFA' : chat.mode === 'collection' ? '#93C5FD' : '#6EE7B7',
                                                border: `1px solid ${chat.mode === 'single' ? 'rgba(139,92,246,0.2)' : chat.mode === 'collection' ? 'rgba(59,130,246,0.2)' : 'rgba(16,185,129,0.2)'}`
                                            }}>
                                                {chat.mode === 'single' ? <FileText size={20} /> : chat.mode === 'collection' ? <Library size={20} /> : <GitCompare size={20} />}
                                            </Box>
                                            <Box sx={{ flex: 1 }}>
                                                <Typography sx={{ fontWeight: 600, fontSize: "1.05rem", color: "#F8FAFC", mb: 0.5 }}>{chat.title}</Typography>
                                                <Typography sx={{ color: "#64748B", fontSize: "0.85rem", display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    {new Date(chat.created_at).toLocaleDateString()} at {new Date(chat.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                    <Box component="span" sx={{ mx: 0.5, opacity: 0.5 }}>•</Box>
                                                    {chat.mode.charAt(0).toUpperCase() + chat.mode.slice(1)} Mode
                                                </Typography>
                                            </Box>
                                            <IconButton size="small" sx={{ color: "#64748B", "&:hover": { color: "#F8FAFC", bgcolor: "rgba(255,255,255,0.1)" } }}><MoreVertical size={20} /></IconButton>
                                        </Box>
                                    ))
                                )}
                            </Box>
                        </motion.div>
                    </Grid>

                    {/* Right Column: Knowledge Base */}
                    <Grid item xs={12} md={4}>
                        <motion.div variants={itemVariants}>
                            <Card sx={{ 
                                bgcolor: "rgba(30,41,59,0.3)", backdropFilter: "blur(20px)",
                                border: "1px solid rgba(255,255,255,0.05)", borderRadius: 4, color: "white",
                                boxShadow: "0 20px 40px -10px rgba(0,0,0,0.4)"
                            }}>
                                <CardContent sx={{ p: 4 }}>
                                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
                                        <Typography variant="h6" sx={{ fontWeight: 600 }}>Library Overview</Typography>
                                        <Button 
                                            size="small" 
                                            startIcon={<FileUp size={16} />} 
                                            onClick={() => window.dispatchEvent(new CustomEvent('open-upload'))}
                                            sx={{ 
                                                bgcolor: "rgba(139,92,246,0.1)", color: "#A78BFA", textTransform: 'none', fontWeight: 600, borderRadius: 2,
                                                "&:hover": { bgcolor: "rgba(139,92,246,0.2)" }
                                            }}
                                        >
                                            Upload
                                        </Button>
                                    </Box>
                                    
                                    <Typography sx={{ color: "#94A3B8", fontSize: "0.85rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", mb: 2 }}>
                                        Recently Added
                                    </Typography>

                                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                                        {recentPapers.length === 0 ? (
                                            <Box sx={{ py: 3, textAlign: "center" }}>
                                                <Typography sx={{ color: "#64748B", fontSize: "0.9rem" }}>Your registry is currently empty.</Typography>
                                            </Box>
                                        ) : (
                                            recentPapers.map((paper, idx) => (
                                                <Box key={idx} sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, group: "hover" }}>
                                                    <Box sx={{ p: 1.2, bgcolor: "rgba(255,255,255,0.05)", borderRadius: 2, border: "1px solid rgba(255,255,255,0.05)" }}>
                                                        <FileText size={18} color="#94A3B8" />
                                                    </Box>
                                                    <Box>
                                                        <Typography sx={{ fontSize: "0.95rem", fontWeight: 500, lineHeight: 1.4, mb: 0.5, color: "#E2E8F0" }}>
                                                            {paper.title || paper.paper_id}
                                                        </Typography>
                                                        <Typography sx={{ fontSize: "0.8rem", color: "#64748B" }}>
                                                            {paper.authors ? (Array.isArray(paper.authors) ? paper.authors.join(", ") : paper.authors) : "Unknown Author"}
                                                        </Typography>
                                                    </Box>
                                                </Box>
                                            ))
                                        )}
                                    </Box>

                                    <Divider sx={{ my: 4, borderColor: "rgba(255,255,255,0.08)" }} />
                                    
                                    <Tooltip title="Full registry view coming soon">
                                        <span>
                                            <Button 
                                                fullWidth 
                                                disabled
                                                endIcon={<Library size={16} />} 
                                                sx={{ 
                                                    textTransform: 'none', color: "#64748B", fontWeight: 500, py: 1.5,
                                                }}
                                            >
                                                View Full Registry
                                            </Button>
                                        </span>
                                    </Tooltip>
                                </CardContent>
                            </Card>
                        </motion.div>
                    </Grid>
                </Grid>
            </Container>
        </Box>
    );
}
