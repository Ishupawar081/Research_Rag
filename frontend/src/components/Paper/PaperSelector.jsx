import { Box, MenuItem, Select, Typography } from "@mui/material";

export default function PaperSelector({ papers, selectedPaperId, onChange }) {
    if (!papers || papers.length === 0) {
        return (
            <Box sx={{ mt: 2, p: 2, bgcolor: "rgba(255,255,255,0.02)", borderRadius: 2 }}>
                <Typography variant="body2" sx={{ color: "#EF4444" }}>No papers available.</Typography>
            </Box>
        );
    }

    return (
        <Box sx={{ mt: 2 }}>
            <Typography variant="caption" sx={{ color: "#94A3B8", mb: 1, display: "block" }}>
                Select Paper
            </Typography>
            <Select
                fullWidth
                value={selectedPaperId || ""}
                onChange={(e) => onChange(e.target.value)}
                displayEmpty
                size="small"
                sx={{
                    color: "#F8FAFC",
                    bgcolor: "rgba(255,255,255,0.02)",
                    "& .MuiOutlinedInput-notchedOutline": {
                        borderColor: "rgba(255,255,255,0.1)",
                    },
                    "&:hover .MuiOutlinedInput-notchedOutline": {
                        borderColor: "rgba(255,255,255,0.2)",
                    },
                    "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                        borderColor: "#A78BFA",
                    },
                    "& .MuiSvgIcon-root": {
                        color: "#94A3B8",
                    },
                    "& .MuiSelect-select": {
                        fontSize: "0.85rem"
                    }
                }}
            >
                <MenuItem value="" disabled>
                    <em style={{ color: "#64748B", fontSize: "0.85rem" }}>Select a paper...</em>
                </MenuItem>
                {papers.map((p) => (
                    <MenuItem key={p.paper_id} value={p.paper_id} sx={{ fontSize: "0.85rem" }}>
                        {p.title.length > 45 ? p.title.slice(0, 45) + "..." : p.title}
                    </MenuItem>
                ))}
            </Select>
        </Box>
    );
}
