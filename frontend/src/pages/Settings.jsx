import { useState } from "react";
import { Box, Typography, Container, Card, GlobalStyles, Tabs, Tab, Button, TextField, Divider, Tooltip } from "@mui/material";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "../contexts/AuthContext";
import Header from "../components/Common/Header";
import { User, Palette, Info, Code, Keyboard, HardDrive, Shield } from "lucide-react";
import { useTheme } from "@mui/material/styles";

export default function Settings() {
    const { user } = useAuth();
    const [tabIndex, setTabIndex] = useState(0);
    const [openaiKey, setOpenaiKey] = useState("");
    const theme = useTheme();

    if (!user) return null;

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } }
    };

    const tabs = [
        { label: "Profile", icon: <User size={18} /> },
        { label: "Theme", icon: <Palette size={18} /> },
        { label: "Storage Usage", icon: <HardDrive size={18} /> },
        { label: "Keyboard Shortcuts", icon: <Keyboard size={18} /> },
        { label: "API Configuration", icon: <Code size={18} /> },
        { label: "About & Version", icon: <Info size={18} /> },
    ];

    return (
        <Box sx={{ minHeight: "100vh", bgcolor: "background.default", color: "text.primary", position: "relative", overflow: "hidden" }}>
            <GlobalStyles styles={{ body: { backgroundColor: theme.palette.background.default } }} />
            
            <Box sx={{
                position: "absolute", top: "-10%", left: "-5%", width: "40vw", height: "40vw",
                background: "radial-gradient(circle, rgba(139,92,246,0.08) 0%, transparent 60%)",
                filter: "blur(80px)", pointerEvents: "none", zIndex: 0
            }} />

            <Box sx={{ position: "relative", zIndex: 10 }}>
                <Header />
            </Box>

            <Container 
                maxWidth="lg" 
                sx={{ mt: 8, position: "relative", zIndex: 1 }}
                component={motion.div}
                variants={containerVariants}
                initial="hidden"
                animate="visible"
            >
                <motion.div variants={itemVariants}>
                    <Typography variant="h4" sx={{ fontWeight: 800, mb: 1, letterSpacing: "-0.02em" }}>Settings</Typography>
                    <Typography sx={{ color: "text.secondary", mb: 6, fontSize: "1.1rem" }}>Manage your account, preferences, and integrations.</Typography>
                </motion.div>

                <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 4 }}>
                    
                    {/* Settings Sidebar */}
                    <Box component={motion.div} variants={itemVariants} sx={{ minWidth: 280 }}>
                        <Card sx={{ 
                            bgcolor: "background.paper", 
                            backdropFilter: "blur(20px)",
                            border: `1px solid ${theme.palette.divider}`, 
                            borderRadius: 4, color: "text.primary",
                        }}>
                            <Tabs 
                                orientation="vertical"
                                value={tabIndex} 
                                onChange={(e, val) => setTabIndex(val)}
                                sx={{
                                    borderRight: 0,
                                    "& .MuiTab-root": { 
                                        color: "text.secondary", textTransform: "none", fontWeight: 600, fontSize: "0.95rem",
                                        alignItems: "flex-start", textAlign: "left", minHeight: 48, py: 2, px: 3,
                                        display: "flex", flexDirection: "row", gap: 2, justifyContent: "flex-start",
                                        borderBottom: `1px solid ${theme.palette.divider}`
                                    },
                                    "& .Mui-selected": { color: `${theme.palette.primary.main} !important`, bgcolor: "rgba(139,92,246,0.05)" },
                                    "& .MuiTabs-indicator": { backgroundColor: theme.palette.primary.main, left: 0, width: 3, borderRadius: "0 4px 4px 0" }
                                }}
                            >
                                {tabs.map((tab, idx) => (
                                    <Tab key={idx} icon={tab.icon} label={tab.label} />
                                ))}
                            </Tabs>
                        </Card>
                    </Box>

                    {/* Settings Content Area */}
                    <Box component={motion.div} variants={itemVariants} sx={{ flex: 1 }}>
                        <Card sx={{ 
                            bgcolor: "background.paper", 
                            backdropFilter: "blur(20px)",
                            border: `1px solid ${theme.palette.divider}`, 
                            borderRadius: 4, color: "text.primary",
                            minHeight: 400
                        }}>
                            <Box sx={{ p: { xs: 3, md: 5 } }}>
                                <AnimatePresence mode="wait">
                                    <motion.div
                                        key={tabIndex}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0, y: -10 }}
                                        transition={{ duration: 0.2 }}
                                    >
                                        
                                        {/* Profile */}
                                        {tabIndex === 0 && (
                                            <Box>
                                                <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>Profile & Account</Typography>
                                                <Typography sx={{ color: "#94A3B8", mb: 4 }}>Manage your personal details and security.</Typography>
                                                <Box sx={{ maxWidth: 500 }}>
                                                    <TextField label="Email Address" value={user.email} disabled fullWidth variant="outlined" sx={{ ...inputStyles, mb: 3 }} />
                                                    <Tooltip title="Password resets coming soon">
                                                        <span><Button variant="outlined" disabled sx={{ textTransform: "none", fontWeight: 600, color: "#94A3B8", borderColor: "rgba(255,255,255,0.1)" }}>Change Password</Button></span>
                                                    </Tooltip>
                                                    <Divider sx={{ my: 4, borderColor: "rgba(255,255,255,0.05)" }} />
                                                    <Typography sx={{ color: "#EF4444", fontWeight: 600, mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}><Shield size={18}/> Danger Zone</Typography>
                                                    <Typography sx={{ color: "#94A3B8", fontSize: "0.85rem", mb: 2 }}>Permanently delete your account and all associated data.</Typography>
                                                    <Tooltip title="Account deletion requires contacting support currently">
                                                        <span><Button variant="outlined" color="error" disabled sx={{ textTransform: "none", fontWeight: 600, borderColor: "rgba(239, 68, 68, 0.3)" }}>Delete Account</Button></span>
                                                    </Tooltip>
                                                </Box>
                                            </Box>
                                        )}

                                        {/* Theme */}
                                        {tabIndex === 1 && (
                                            <Box>
                                                <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>Appearance</Typography>
                                                <Typography sx={{ color: "#94A3B8", mb: 4 }}>Customize the look and feel of your workspace.</Typography>
                                                <Box sx={{ p: 3, border: "1px solid rgba(139,92,246,0.3)", borderRadius: 2, bgcolor: "rgba(139,92,246,0.05)", display: "inline-block", mb: 3 }}>
                                                    <Typography sx={{ color: "#A78BFA", fontWeight: 600 }}>System Dark Mode Active</Typography>
                                                </Box>
                                                <Typography sx={{ color: "#64748B", fontSize: "0.9rem" }}>Light mode and custom accent colors are currently in development.</Typography>
                                            </Box>
                                        )}

                                        {/* Storage Usage */}
                                        {tabIndex === 2 && (
                                            <Box>
                                                <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>Storage & Limits</Typography>
                                                <Typography sx={{ color: "#94A3B8", mb: 4 }}>View your current knowledge base footprint.</Typography>
                                                <Box sx={{ maxWidth: 500, p: 3, bgcolor: "rgba(0,0,0,0.2)", borderRadius: 2, border: "1px solid rgba(255,255,255,0.05)" }}>
                                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                                        <Typography sx={{ fontWeight: 500 }}>Vector Storage</Typography>
                                                        <Typography sx={{ color: "#A78BFA" }}>0.05 GB / 1 GB</Typography>
                                                    </Box>
                                                    <Box sx={{ width: '100%', height: 6, bgcolor: "rgba(255,255,255,0.1)", borderRadius: 3, overflow: 'hidden' }}>
                                                        <Box sx={{ width: '5%', height: '100%', bgcolor: "#A78BFA", borderRadius: 3 }} />
                                                    </Box>
                                                    <Typography sx={{ color: "#64748B", fontSize: "0.8rem", mt: 2, fontStyle: "italic" }}>Metrics are currently simulated.</Typography>
                                                </Box>
                                            </Box>
                                        )}

                                        {/* Keyboard Shortcuts */}
                                        {tabIndex === 3 && (
                                            <Box>
                                                <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>Keyboard Shortcuts</Typography>
                                                <Typography sx={{ color: "#94A3B8", mb: 4 }}>Navigate the system faster.</Typography>
                                                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, maxWidth: 400 }}>
                                                    {[
                                                        { label: "Global Search", keys: ["Cmd", "K"] },
                                                        { label: "New Chat", keys: ["Cmd", "N"] },
                                                        { label: "Upload PDF", keys: ["Cmd", "U"] },
                                                        { label: "Close Modal", keys: ["Esc"] }
                                                    ].map((s, i) => (
                                                        <Box key={i} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', py: 1, borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                                                            <Typography sx={{ color: "#E2E8F0" }}>{s.label}</Typography>
                                                            <Box sx={{ display: 'flex', gap: 1 }}>
                                                                {s.keys.map((k, j) => (
                                                                    <Box key={j} sx={{ px: 1, py: 0.5, bgcolor: "rgba(255,255,255,0.1)", borderRadius: 1, fontSize: "0.8rem", color: "#94A3B8", fontFamily: "monospace" }}>
                                                                        {k}
                                                                    </Box>
                                                                ))}
                                                            </Box>
                                                        </Box>
                                                    ))}
                                                    <Typography sx={{ color: "#64748B", fontSize: "0.8rem", mt: 2, fontStyle: "italic" }}>Shortcuts are preview-only in this release.</Typography>
                                                </Box>
                                            </Box>
                                        )}

                                        {/* API Configuration */}
                                        {tabIndex === 4 && (
                                            <Box>
                                                <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>API Configuration</Typography>
                                                <Typography sx={{ color: "#94A3B8", mb: 4 }}>Connect your own keys to override system defaults.</Typography>
                                                <Box sx={{ maxWidth: 500 }}>
                                                    <TextField label="OpenAI API Key" placeholder="sk-..." value={openaiKey} onChange={(e) => setOpenaiKey(e.target.value)} fullWidth variant="outlined" sx={inputStyles} type="password" />
                                                    <Button sx={{ mt: 3, bgcolor: "rgba(139,92,246,0.2)", color: "#A78BFA", textTransform: 'none', fontWeight: 600, "&:hover": { bgcolor: "rgba(139,92,246,0.3)" } }}>Save Configuration</Button>
                                                </Box>
                                            </Box>
                                        )}

                                        {/* About & Version */}
                                        {tabIndex === 5 && (
                                            <Box>
                                                <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>About the System</Typography>
                                                <Typography sx={{ color: "#94A3B8", mb: 4 }}>System information and open source credits.</Typography>
                                                
                                                <Box sx={{ mb: 4 }}>
                                                    <Typography sx={{ color: "#F8FAFC", fontWeight: 600 }}>Version</Typography>
                                                    <Typography sx={{ color: "#94A3B8" }}>v1.0.0-beta (Production Ready)</Typography>
                                                </Box>
                                                <Box sx={{ mb: 4 }}>
                                                    <Typography sx={{ color: "#F8FAFC", fontWeight: 600 }}>GitHub Repository</Typography>
                                                    <Typography sx={{ color: "#3B82F6", cursor: "pointer", "&:hover": { textDecoration: "underline" } }}>github.com/organization/rag-project</Typography>
                                                </Box>
                                                <Box>
                                                    <Typography sx={{ color: "#F8FAFC", fontWeight: 600 }}>License</Typography>
                                                    <Typography sx={{ color: "#94A3B8" }}>MIT License - Internal Use</Typography>
                                                </Box>
                                            </Box>
                                        )}
                                        
                                    </motion.div>
                                </AnimatePresence>
                            </Box>
                        </Card>
                    </Box>

                </Box>
            </Container>
        </Box>
    );
}

const inputStyles = {
    "& .MuiOutlinedInput-root": {
        bgcolor: "rgba(0,0,0,0.2)",
        color: "white",
        borderRadius: 2,
        "& fieldset": { borderColor: "rgba(255,255,255,0.1)" },
        "&:hover fieldset": { borderColor: "rgba(255,255,255,0.2)" },
        "&.Mui-focused fieldset": { borderColor: "#A78BFA" },
        "&.Mui-disabled fieldset": { borderColor: "rgba(255,255,255,0.05)" },
        "&.Mui-disabled": { color: "#64748B", WebkitTextFillColor: "#94A3B8" }
    },
    "& .MuiInputLabel-root": { color: "#94A3B8" },
    "& .MuiInputLabel-root.Mui-focused": { color: "#A78BFA" }
};
