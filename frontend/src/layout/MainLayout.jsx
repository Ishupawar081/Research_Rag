import { useState, useEffect } from "react";
import { Box, GlobalStyles } from "@mui/material";
import { motion } from "framer-motion";
import { api } from "../api/chat";
import { supabase } from "../lib/supabase";
import { useAuth } from "../contexts/AuthContext";
import { useTheme } from "@mui/material/styles";

import Header from "../components/Common/Header";
import Sidebar from "../components/Sidebar/Sidebar";
import ChatBox from "../components/Chat/ChatBox";
import SourcePanel from "../components/Chat/SourcePanel";

export default function MainLayout() {
    const { user } = useAuth();
    const theme = useTheme();
    const [papers, setPapers] = useState([]);
    const [indexedCount, setIndexedCount] = useState(0);
    const [registryStatus, setRegistryStatus] = useState("loading"); // loading, error, success, empty
    const [sources, setSources] = useState([]);
    
    const [chatHistory, setChatHistory] = useState([]);
    const [activeChatId, setActiveChatId] = useState(null);
    const [modelInfo, setModelInfo] = useState({ llm: "Unknown", embedding: "Unknown" });
    
    // Shared chat configuration across Sidebar and ChatBox
    const [chatConfig, setChatConfig] = useState({
        mode: "collection", // 'single', 'collection', 'compare'
        paperA: null,       // selected paper_id for Single/Compare mode
        paperB: null        // second selected paper_id for Compare mode
    });
    
    const fetchPapers = async () => {
        setRegistryStatus("loading");
        try {
            const res = await api.get("/papers");
            if (res.data && res.data.papers) {
                setPapers(res.data.papers);
                setIndexedCount(res.data.papers.length);
                setRegistryStatus(res.data.papers.length === 0 ? "empty" : "success");
            } else {
                setRegistryStatus("empty");
            }
        } catch (error) {
            console.error("Failed to fetch papers", error);
            setRegistryStatus("error");
        }
    };

    useEffect(() => {
        fetchPapers();
        
        api.get("/info")
            .then(res => {
                setModelInfo({ 
                    llm: res.data.llm_model || "Unknown", 
                    embedding: res.data.embedding_model || "Unknown" 
                });
            })
            .catch(() => {
                // Keep default Unknown
            });

        if (user) {
            supabase.from('chats')
                .select('*')
                .eq('user_id', user.id)
                .order('created_at', { ascending: false })
                .then(({ data }) => {
                    if (data) setChatHistory(data);
                });
        }
    }, [user]);

    const handleUpdateHistory = async (chatData) => {
        // Save to Supabase
        if (user) {
            const chatToSave = { ...chatData, user_id: user.id };
            // Optional: you can remove 'sources' or 'messages' from chatData if not in the DB schema
            
            await supabase.from('chats')
                .upsert([chatToSave], { onConflict: 'id' });
        }

        setChatHistory(prev => {
            const existingIdx = prev.findIndex(c => c.id === chatData.id);
            let updated;
            if (existingIdx >= 0) {
                updated = [...prev];
                updated[existingIdx] = chatData;
            } else {
                updated = [chatData, ...prev];
            }
            return updated;
        });
    };

    const handleNewChat = () => {
        setActiveChatId(null);
        setSources([]);
        // Do not reset mode or papers as requested
    };

    const handleSelectChat = (chat) => {
        setActiveChatId(chat.id);
        setChatConfig({
            mode: chat.mode,
            paperA: chat.paperA,
            paperB: chat.paperB
        });
        setSources(chat.sources || []);
    };

    const [globalSearchQuery, setGlobalSearchQuery] = useState("");

    return (
        <Box
            component={motion.div}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
            sx={{
                height: "100vh",
                bgcolor: "background.default", 
                overflow: "hidden",
                display: "flex",
                flexDirection: "column",
                position: "relative",
            }}
        >
            <GlobalStyles styles={{
                "*::-webkit-scrollbar": {
                    width: "8px",
                    height: "8px",
                },
                "*::-webkit-scrollbar-track": {
                    background: "transparent",
                },
                "*::-webkit-scrollbar-thumb": {
                    backgroundColor: theme.palette.mode === 'dark' ? "rgba(255, 255, 255, 0.1)" : "rgba(0, 0, 0, 0.1)",
                    borderRadius: "10px",
                    border: `2px solid ${theme.palette.background.default}`, // Creates padding around the scrollbar
                },
                "*::-webkit-scrollbar-thumb:hover": {
                    backgroundColor: theme.palette.mode === 'dark' ? "rgba(255, 255, 255, 0.2)" : "rgba(0, 0, 0, 0.2)",
                }
            }} />

            {/* Glowing Ambient Orbs for Premium Vibe */}
            <Box sx={{
                position: "absolute", top: "-10%", left: "-5%", width: "40vw", height: "40vw",
                background: "radial-gradient(circle, rgba(139,92,246,0.06) 0%, transparent 60%)",
                filter: "blur(80px)", pointerEvents: "none", zIndex: 0
            }} />
            <Box sx={{
                position: "absolute", bottom: "-10%", right: "-5%", width: "40vw", height: "40vw",
                background: "radial-gradient(circle, rgba(59,130,246,0.06) 0%, transparent 60%)",
                filter: "blur(80px)", pointerEvents: "none", zIndex: 0
            }} />

            <Box sx={{ position: "relative", zIndex: 10 }}>
                <Header 
                    searchQuery={globalSearchQuery}
                    onSearchChange={setGlobalSearchQuery}
                />
            </Box>

            <Box
                sx={{
                    flex: 1,
                    position: "relative",
                    zIndex: 10,
                    display: "grid",
                    gridTemplateColumns: {
                        xs: "1fr",
                        md: "260px 1fr",
                        lg: "280px 1fr 340px"
                    },
                    gap: { xs: 2, lg: 3 },
                    p: { xs: 2, lg: 3 },
                    pt: { xs: 2, lg: 2 }, // slightly less top padding so it tucks nicely under the header
                    overflow: "hidden",
                    minHeight: 0,
                    minWidth: 0
                }}
            >
                {/* Sidebar Column */}
                <Box sx={{
                    display: { xs: "none", md: "block" },
                    bgcolor: "background.paper", 
                    borderRadius: "20px",
                    border: `1px solid ${theme.palette.divider}`,
                    boxShadow: theme.palette.mode === 'dark' ? "0 20px 40px -10px rgba(0, 0, 0, 0.5)" : "0 20px 40px -10px rgba(0, 0, 0, 0.05)",
                    overflow: "hidden"
                }}>
                    <Sidebar 
                        indexedCount={indexedCount} 
                        onUploadComplete={fetchPapers} 
                        chatHistory={chatHistory} 
                        onSelectChat={handleSelectChat}
                        onNewChat={handleNewChat}
                        activeChatId={activeChatId}
                        papers={papers}
                        registryStatus={registryStatus}
                        chatConfig={chatConfig}
                        setChatConfig={setChatConfig}
                        globalSearchQuery={globalSearchQuery}
                        modelInfo={modelInfo}
                    />
                </Box>

                {/* Main Chat Workspace */}
                <Box sx={{
                    bgcolor: "background.paper", 
                    borderRadius: "24px",
                    border: `1px solid ${theme.palette.divider}`,
                    boxShadow: theme.palette.mode === 'dark' ? "0 20px 50px -10px rgba(0, 0, 0, 0.6)" : "0 20px 50px -10px rgba(0, 0, 0, 0.08)",
                    overflow: "hidden",
                    display: "flex",
                    flexDirection: "column",
                    minHeight: 0,
                    minWidth: 0
                }}>
                    <ChatBox 
                        onSourcesUpdate={setSources} 
                        activeChatId={activeChatId}
                        setActiveChatId={setActiveChatId}
                        onUpdateHistory={handleUpdateHistory}
                        chatConfig={chatConfig}
                        papers={papers}
                        onNewChat={handleNewChat}
                        chatHistory={chatHistory}
                    />
                </Box>

                {/* Source Panel Column */}
                <Box sx={{
                    display: { xs: "none", lg: "block" },
                    bgcolor: "background.paper",
                    borderRadius: "20px",
                    border: `1px solid ${theme.palette.divider}`,
                    boxShadow: theme.palette.mode === 'dark' ? "0 20px 40px -10px rgba(0, 0, 0, 0.5)" : "0 20px 40px -10px rgba(0, 0, 0, 0.05)",
                    overflow: "hidden"
                }}>
                    <SourcePanel 
                        sources={sources} 
                        chatConfig={chatConfig}
                        papers={papers}
                    />
                </Box>

            </Box>
        </Box>
    );
}