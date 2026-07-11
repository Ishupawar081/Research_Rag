import { useState } from "react";
import { Paper, InputBase, IconButton } from "@mui/material";
import { Send, Paperclip } from "lucide-react";

export default function ChatInput({ onSend, disabled }) {
    const [text, setText] = useState("");

    const handleSend = () => {
        if (!text.trim() || disabled) return;
        onSend(text);
        setText("");
    };

    return (
        <Paper
            elevation={0}
            sx={{
                p: "8px 12px",
                borderRadius: "24px",
                display: "flex",
                alignItems: "center",
                gap: 1.5,
                bgcolor: "rgba(30, 41, 59, 0.7)",
                backdropFilter: "blur(20px)",
                border: "1px solid rgba(255, 255, 255, 0.1)",
                boxShadow: "0 -10px 40px rgba(0,0,0,0.2), 0 10px 20px rgba(0,0,0,0.3)",
                transition: "all 0.3s ease",
                "&:focus-within": {
                    borderColor: "rgba(139,92,246,0.5)",
                    bgcolor: "rgba(30, 41, 59, 0.9)",
                    boxShadow: "0 0 0 4px rgba(139,92,246,0.1), 0 -10px 40px rgba(0,0,0,0.3)",
                }
            }}
        >
            <IconButton sx={{ color: "#64748B", "&:hover": { color: "#F8FAFC", bgcolor: "rgba(255,255,255,0.05)" } }}>
                <Paperclip size={20} />
            </IconButton>

            <InputBase
                fullWidth
                placeholder="Ask anything about research papers..."
                value={text}
                disabled={disabled}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSend();
                    }
                }}
                sx={{
                    color: "#F8FAFC",
                    fontSize: "1rem",
                    "& input::placeholder": {
                        color: "#64748B",
                        opacity: 1,
                    }
                }}
            />

            <IconButton 
                disabled={!text.trim() || disabled}
                onClick={handleSend}
                sx={{ 
                    bgcolor: text.trim() && !disabled ? "#3B82F6" : "rgba(255,255,255,0.05)",
                    color: text.trim() && !disabled ? "#FFFFFF" : "#64748B",
                    borderRadius: "16px",
                    p: 1.2,
                    transition: "all 0.2s",
                    "&:hover": { 
                        bgcolor: text.trim() && !disabled ? "#2563EB" : "rgba(255,255,255,0.05)",
                        transform: text.trim() && !disabled ? "scale(1.05)" : "none"
                    }
                }}
            >
                <Send size={18} style={{ transform: "translateX(1px)" }} />
            </IconButton>
        </Paper>
    );
}