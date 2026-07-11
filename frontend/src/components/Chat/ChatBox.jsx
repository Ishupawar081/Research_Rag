import { useState, useEffect } from "react";
import { chat } from "../../api/chat";
import { Box } from "@mui/material";

import ChatHeader from "./ChatHeader";
import ChatInput from "./ChatInput";
import ChatMessagesList from "./ChatMessagesList";
import ExportModal from "./ExportModal";

export default function ChatBox({ onSourcesUpdate, activeChatId, setActiveChatId, onUpdateHistory, chatConfig, papers, onNewChat, chatHistory }) {
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);

    // Load active chat when it changes
    useEffect(() => {
        if (activeChatId) {
            const activeChat = chatHistory.find(c => c.id === activeChatId);
            if (activeChat) {
                setMessages(activeChat.messages || []);
            } else {
                // If not found in history, it might be a brand new optimistic chat.
                // Only clear if we don't already have optimistic messages for this session.
                setMessages(prev => prev.length > 0 ? prev : []);
            }
        } else {
            setMessages([]);
        }
    }, [activeChatId]);

    const send = async (text) => {
        if (!text.trim()) return;

        if (chatConfig.mode === "single" && !chatConfig.paperA) {
            setMessages([...messages, { role: "user", text }, { role: "assistant", text: "Please select a paper first." }]);
            return;
        }
        if (chatConfig.mode === "compare" && (!chatConfig.paperA || !chatConfig.paperB || chatConfig.paperA === chatConfig.paperB)) {
            setMessages([...messages, { role: "user", text }, { role: "assistant", text: "Please select two different papers to compare." }]);
            return;
        }

        let chatId = activeChatId;
        const isNewChat = messages.length === 0 || !activeChatId;
        
        if (isNewChat) {
            chatId = Date.now().toString(); // simple ID
            setActiveChatId(chatId);
        }

        const userMessage = { role: "user", text };
        const newMessages = [...messages, userMessage];
        setMessages(newMessages);
        setLoading(true);
        
        // Sync to history immediately for user message
        const chatTitle = isNewChat ? (text.length > 30 ? text.slice(0, 30) + "..." : text) : (chatHistory.find(c => c.id === chatId)?.title || text);
        
        const syncHistory = (msgs, currentSources = undefined) => {
            const existingChat = chatHistory.find(c => c.id === chatId);
            const sourcesToSave = currentSources !== undefined ? currentSources : (existingChat?.sources || []);

            onUpdateHistory({
                id: chatId,
                title: chatTitle,
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                mode: chatConfig.mode,
                paperA: chatConfig.paperA,
                paperB: chatConfig.paperB,
                messages: msgs,
                sources: sourcesToSave
            });
        };
        
        syncHistory(newMessages);

        try {
            const payload = {
                mode: chatConfig.mode,
                query: text
            };
            if (chatConfig.mode === "single") {
                payload.paper = chatConfig.paperA;
            } else if (chatConfig.mode === "compare") {
                payload.paper_a = chatConfig.paperA;
                payload.paper_b = chatConfig.paperB;
            }

            const response = await chat(payload);

            let assistantText = "";
            let newSources = undefined;
            if (response.success) {
                assistantText = response.answer;
                if (response.sources) {
                    newSources = response.sources;
                    if (onSourcesUpdate) {
                        onSourcesUpdate(newSources);
                    }
                }
            } else {
                assistantText = response.error || "An unknown error occurred.";
            }
            
            const finalMessages = [...newMessages, { role: "assistant", text: assistantText }];
            setMessages(finalMessages);
            syncHistory(finalMessages, newSources);

        } catch (err) {
            const finalMessages = [...newMessages, { role: "assistant", text: "Unable to connect to backend." }];
            setMessages(finalMessages);
            syncHistory(finalMessages);
        } finally {
            setLoading(false);
        }
    };

    const formatMode = (m) => {
        if (m === "single") return "Single Paper";
        if (m === "compare") return "Compare Papers";
        return "Collection";
    };

    let headerPaperTitle = null;
    let headerPaperTitle2 = null;
    if (chatConfig.mode === "single" && chatConfig.paperA) {
        const p = papers.find(x => x.paper_id === chatConfig.paperA);
        if (p) headerPaperTitle = p.title.length > 40 ? p.title.slice(0, 40) + "..." : p.title;
    } else if (chatConfig.mode === "compare" && chatConfig.paperA && chatConfig.paperB) {
        const pA = papers.find(x => x.paper_id === chatConfig.paperA);
        const pB = papers.find(x => x.paper_id === chatConfig.paperB);
        if (pA && pB) {
            headerPaperTitle = pA.title.length > 25 ? pA.title.slice(0, 25) + "..." : pA.title;
            headerPaperTitle2 = pB.title.length > 25 ? pB.title.slice(0, 25) + "..." : pB.title;
        }
    }

    return (
        <Box sx={{ flex: 1, display: "flex", flexDirection: "column", height: "100%" }}>
            <ChatHeader 
                mode={formatMode(chatConfig.mode)} 
                paper={headerPaperTitle} 
                paper2={headerPaperTitle2}
                onNewChat={onNewChat} 
                onClear={onNewChat} 
            />

            <ChatMessagesList 
                messages={messages} 
                loading={loading} 
                onSend={send}
                mode={chatConfig.mode}
            />

            <Box sx={{ p: { xs: 2, md: 3 }, pt: 0 }}>
                <ChatInput onSend={send} disabled={loading} />
            </Box>

            <ExportModal messages={messages} chatConfig={chatConfig} papers={papers} />
        </Box>
    );
}