import { Box } from "@mui/material";
import { useEffect, useRef } from "react";
import Welcome from "./Welcome";
import ChatMessage from "./ChatMessage";
import TypingIndicator from "../Common/TypingIndicator";

export default function ChatMessagesList({ messages, loading, onSend, mode }) {
    const bottomRef = useRef(null);

    useEffect(() => {
        // Only scroll if we just added a message or loading state changed
        bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    }, [messages.length, loading]);

    return (
        <Box sx={{ flex: 1, overflowY: "auto", p: { xs: 2, md: 4 }, "&::-webkit-scrollbar": { display: "none" }, scrollbarWidth: "none" }}>
            {messages.length === 0 ? (
                <Welcome onSelect={onSend} mode={mode} />
            ) : (
                <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
                    {messages.map((m, index) => (
                        <ChatMessage
                            key={index}
                            role={m.role}
                            text={m.text}
                            timestamp={new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        />
                    ))}
                    {loading && <TypingIndicator />}
                    <div ref={bottomRef} style={{ height: 1 }} />
                </Box>
            )}
        </Box>
    );
}
