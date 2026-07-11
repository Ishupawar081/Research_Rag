import { useState, useEffect } from "react";
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Box, Typography, RadioGroup, FormControlLabel, Radio } from "@mui/material";
import { Download } from "lucide-react";
import { jsPDF } from "jspdf";

export default function ExportModal({ messages, chatConfig, papers }) {
    const [open, setOpen] = useState(false);
    const [format, setFormat] = useState("markdown");

    useEffect(() => {
        const handleOpen = () => setOpen(true);
        window.addEventListener('export-chat', handleOpen);
        return () => window.removeEventListener('export-chat', handleOpen);
    }, []);

    const getChatMetadata = () => {
        let meta = `AI Research Assistant Export\nDate: ${new Date().toLocaleString()}\nMode: ${chatConfig.mode}\n\n`;
        if (chatConfig.mode === "single" && chatConfig.paperA) {
            const p = papers.find(x => x.paper_id === chatConfig.paperA);
            if (p) meta += `Paper: ${p.title}\n`;
        } else if (chatConfig.mode === "compare" && chatConfig.paperA && chatConfig.paperB) {
            const pA = papers.find(x => x.paper_id === chatConfig.paperA);
            const pB = papers.find(x => x.paper_id === chatConfig.paperB);
            if (pA) meta += `Paper A: ${pA.title}\n`;
            if (pB) meta += `Paper B: ${pB.title}\n`;
        }
        meta += `\n---\n\n`;
        return meta;
    };

    const handleExport = () => {
        const meta = getChatMetadata();
        let content = meta;
        
        messages.forEach(m => {
            content += `**${m.role === 'user' ? 'You' : 'AI'}**:\n${m.text}\n\n`;
        });

        if (format === "txt" || format === "markdown") {
            const ext = format === "txt" ? "txt" : "md";
            const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = `chat_export.${ext}`;
            link.click();
            URL.revokeObjectURL(url);
        } else if (format === "pdf") {
            const doc = new jsPDF();
            const splitText = doc.splitTextToSize(content.replace(/\*\*/g, ""), 180);
            
            let y = 10;
            splitText.forEach(line => {
                if (y > 280) {
                    doc.addPage();
                    y = 10;
                }
                doc.text(line, 10, y);
                y += 7;
            });
            doc.save("chat_export.pdf");
        }
        setOpen(false);
    };

    return (
        <Dialog 
            open={open} 
            onClose={() => setOpen(false)}
            PaperProps={{
                sx: { bgcolor: "#111827", color: "white", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 3, minWidth: 400 }
            }}
        >
            <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1.5, pb: 1 }}>
                <Download size={20} color="#A78BFA" />
                Export Conversation
            </DialogTitle>
            <DialogContent sx={{ pb: 1 }}>
                <Typography sx={{ color: "#94A3B8", mb: 3, fontSize: "0.9rem" }}>
                    Choose a format to save your research conversation.
                </Typography>
                <RadioGroup value={format} onChange={(e) => setFormat(e.target.value)}>
                    <FormControlLabel value="markdown" control={<Radio sx={{ color: "#64748B", "&.Mui-checked": { color: "#A78BFA" } }} />} label="Markdown (.md)" />
                    <FormControlLabel value="txt" control={<Radio sx={{ color: "#64748B", "&.Mui-checked": { color: "#A78BFA" } }} />} label="Plain Text (.txt)" />
                    <FormControlLabel value="pdf" control={<Radio sx={{ color: "#64748B", "&.Mui-checked": { color: "#A78BFA" } }} />} label="PDF Document (.pdf)" />
                </RadioGroup>
            </DialogContent>
            <DialogActions sx={{ p: 3, pt: 1 }}>
                <Button onClick={() => setOpen(false)} sx={{ color: "#94A3B8", textTransform: 'none' }}>Cancel</Button>
                <Button onClick={handleExport} variant="contained" sx={{ bgcolor: "#8B5CF6", "&:hover": { bgcolor: "#7C3AED" }, textTransform: 'none', borderRadius: 2 }}>
                    Download
                </Button>
            </DialogActions>
        </Dialog>
    );
}
