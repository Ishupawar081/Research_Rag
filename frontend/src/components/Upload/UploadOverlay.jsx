import { useState, useRef } from "react";
import { Box, Typography, LinearProgress, Paper, IconButton } from "@mui/material";
import { motion, AnimatePresence } from "framer-motion";
import { X, UploadCloud, Rocket } from "lucide-react";
import { supabase } from "../../lib/supabase";
import { API_URL } from "../../config/api";

export default function UploadOverlay({ open, onClose, onComplete }) {
    const [file, setFile] = useState(null);
    const [progress, setProgress] = useState(0);
    const [message, setMessage] = useState("");
    const [isUploading, setIsUploading] = useState(false);
    const [hasError, setHasError] = useState(false);
    const fileInputRef = useRef(null);

    const handleFileSelect = (e) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setIsUploading(true);
        setHasError(false);
        setProgress(0);
        setMessage("Initializing hyperspace jump...");

        const formData = new FormData();
        formData.append("file", file);

        try {
            const { data: { session } } = await supabase.auth.getSession();
            const headers = {};
            if (session?.access_token) {
                headers["Authorization"] = `Bearer ${session.access_token}`;
            }

            const response = await fetch(`${API_URL}/upload`, {
                method: "POST",
                headers,
                body: formData,
            });

            if (!response.ok) {
                let errorMsg = `Upload failed with status ${response.status}`;
                try {
                    const errData = await response.json();
                    errorMsg = errData.detail || errData.error || errorMsg;
                } catch (e) {
                    // ignore JSON parse error
                }
                throw new Error(errorMsg);
            }

            if (!response.body) throw new Error("No readable stream available");

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            
            let buffer = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n\n");
                
                // Keep the last partial chunk in the buffer
                buffer = lines.pop() || "";

                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            if (data.progress !== undefined) {
                                setProgress(data.progress);
                            }
                            if (data.message) {
                                setMessage(data.message);
                            }
                            if (data.stage === "complete") {
                                setTimeout(() => {
                                    setIsUploading(false);
                                    setFile(null);
                                    if (onComplete) onComplete();
                                    onClose();
                                }, 2000);
                            }
                            if (data.stage === "error") {
                                setHasError(true);
                                setMessage(data.message || "An error occurred during upload.");
                                setProgress(0);
                            }
                        } catch (e) {
                            console.error("Error parsing SSE:", e);
                        }
                    }
                }
            }
        } catch (error) {
            console.error("Upload failed", error);
            setMessage(error.message || "Error connecting to mission control.");
            setHasError(true);
        }
    };

    return (
        <AnimatePresence>
            {open && (
                <Box
                    component={motion.div}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    sx={{
                        position: "fixed",
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        zIndex: 9999,
                        bgcolor: "rgba(11, 17, 32, 0.8)",
                        backdropFilter: "blur(12px)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center"
                    }}
                >
                    <Paper
                        component={motion.div}
                        initial={{ scale: 0.9, y: 20 }}
                        animate={{ scale: 1, y: 0 }}
                        exit={{ scale: 0.9, y: 20 }}
                        sx={{
                            width: "100%",
                            maxWidth: 500,
                            p: 4,
                            bgcolor: "rgba(30, 41, 59, 0.95)",
                            border: "1px solid rgba(139, 92, 246, 0.3)",
                            boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.5)",
                            position: "relative",
                            overflow: "hidden"
                        }}
                    >
                        {/* Decorative Gradient Blob */}
                        <Box
                            sx={{
                                position: "absolute",
                                top: -50,
                                right: -50,
                                width: 150,
                                height: 150,
                                bgcolor: "rgba(139, 92, 246, 0.2)",
                                filter: "blur(40px)",
                                borderRadius: "50%",
                                zIndex: 0
                            }}
                        />

                        <IconButton
                            onClick={onClose}
                            disabled={isUploading}
                            sx={{ position: "absolute", top: 16, right: 16, color: "#94A3B8" }}
                        >
                            <X size={20} />
                        </IconButton>

                        <Typography variant="h5" sx={{ fontWeight: 600, color: "#F8FAFC", mb: 1, position: "relative", zIndex: 1 }}>
                            Upload Research Paper
                        </Typography>
                        <Typography variant="body2" sx={{ color: "#94A3B8", mb: 4, position: "relative", zIndex: 1 }}>
                            Ingest a new PDF into your knowledge universe.
                        </Typography>

                        {!isUploading ? (
                            <Box sx={{ position: "relative", zIndex: 1 }}>
                                <input
                                    type="file"
                                    accept=".pdf"
                                    hidden
                                    ref={fileInputRef}
                                    onChange={handleFileSelect}
                                />
                                <Box
                                    onClick={() => fileInputRef.current?.click()}
                                    sx={{
                                        border: "2px dashed rgba(139, 92, 246, 0.4)",
                                        borderRadius: 2,
                                        p: 4,
                                        textAlign: "center",
                                        cursor: "pointer",
                                        bgcolor: "rgba(139, 92, 246, 0.05)",
                                        transition: "all 0.2s",
                                        "&:hover": {
                                            bgcolor: "rgba(139, 92, 246, 0.1)",
                                            borderColor: "rgba(139, 92, 246, 0.6)"
                                        },
                                        mb: 3
                                    }}
                                >
                                    <UploadCloud size={40} color="#A78BFA" style={{ marginBottom: 16 }} />
                                    <Typography sx={{ color: "#E2E8F0", fontWeight: 500 }}>
                                        {file ? file.name : "Click to select a PDF"}
                                    </Typography>
                                </Box>

                                <Box sx={{ display: "flex", justifyContent: "flex-end" }}>
                                    <Box
                                        component="button"
                                        onClick={handleUpload}
                                        disabled={!file}
                                        sx={{
                                            bgcolor: file ? "#8B5CF6" : "rgba(139, 92, 246, 0.5)",
                                            color: "#fff",
                                            border: "none",
                                            py: 1.5,
                                            px: 4,
                                            borderRadius: 1.5,
                                            fontWeight: 600,
                                            cursor: file ? "pointer" : "not-allowed",
                                            display: "flex",
                                            alignItems: "center",
                                            gap: 1,
                                            transition: "background 0.2s",
                                            "&:hover": {
                                                bgcolor: file ? "#7C3AED" : "rgba(139, 92, 246, 0.5)"
                                            }
                                        }}
                                    >
                                        <Rocket size={18} />
                                        Launch Ingestion
                                    </Box>
                                </Box>
                            </Box>
                        ) : (
                            <Box sx={{ position: "relative", zIndex: 1, py: 2 }}>
                                <Box sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}>
                                    <Typography variant="body2" sx={{ color: hasError ? "#EF4444" : "#E2E8F0", fontWeight: 500 }}>
                                        {message}
                                    </Typography>
                                    {!hasError && (
                                        <Typography variant="body2" sx={{ color: "#A78BFA", fontWeight: 600 }}>
                                            {progress}%
                                        </Typography>
                                    )}
                                </Box>
                                {!hasError && (
                                    <LinearProgress 
                                        variant="determinate" 
                                        value={progress} 
                                        sx={{ 
                                            height: 8, 
                                            borderRadius: 4,
                                            bgcolor: "rgba(255,255,255,0.1)",
                                            "& .MuiLinearProgress-bar": {
                                                bgcolor: "#8B5CF6",
                                                borderRadius: 4
                                            }
                                        }} 
                                    />
                                )}
                                {hasError ? (
                                    <Box sx={{ mt: 3, display: "flex", justifyContent: "flex-end" }}>
                                        <Box
                                            component="button"
                                            onClick={() => {
                                                setHasError(false);
                                                setIsUploading(false);
                                                setFile(null);
                                            }}
                                            sx={{
                                                bgcolor: "transparent",
                                                color: "#EF4444",
                                                border: "1px solid rgba(239, 68, 68, 0.5)",
                                                py: 1,
                                                px: 3,
                                                borderRadius: 1.5,
                                                fontWeight: 600,
                                                cursor: "pointer",
                                                "&:hover": {
                                                    bgcolor: "rgba(239, 68, 68, 0.1)"
                                                }
                                            }}
                                        >
                                            Dismiss
                                        </Box>
                                    </Box>
                                ) : (
                                    <Typography variant="caption" sx={{ color: "#64748B", display: "block", mt: 2, textAlign: "center" }}>
                                        This may take a few minutes depending on the paper's size.
                                    </Typography>
                                )}
                            </Box>
                        )}
                    </Paper>
                </Box>
            )}
        </AnimatePresence>
    );
}
