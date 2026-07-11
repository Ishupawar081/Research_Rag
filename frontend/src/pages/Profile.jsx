import { Box, Typography, Container, Card, CardContent, Avatar, Grid, Divider, GlobalStyles } from "@mui/material";
import { motion } from "framer-motion";
import { useAuth } from "../contexts/AuthContext";
import { User, Mail, Calendar, Key, ShieldCheck, Clock } from "lucide-react";
import Header from "../components/Common/Header";
import { useTheme } from "@mui/material/styles";

export default function Profile() {
    const { user } = useAuth();
    const theme = useTheme();

    if (!user) return null;

    const fullName = user.user_metadata?.full_name || user.email?.split('@')[0] || "Researcher";
    const email = user.email || "";
    const avatarUrl = user.user_metadata?.avatar_url || "";
    const initials = fullName.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
    const provider = user.app_metadata?.provider === "google" ? "Google OAuth" : "Email / Password";
    const memberSince = new Date(user.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });
    const lastLogin = new Date(user.last_sign_in_at).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } }
    };

    return (
        <Box sx={{ minHeight: "100vh", bgcolor: "background.default", color: "text.primary", position: "relative", overflow: "hidden" }}>
            <GlobalStyles styles={{ body: { backgroundColor: theme.palette.background.default } }} />
            
            {/* Ambient Background Glows */}
            <Box sx={{
                position: "absolute", top: "-10%", left: "-5%", width: "40vw", height: "40vw",
                background: "radial-gradient(circle, rgba(139,92,246,0.08) 0%, transparent 60%)",
                filter: "blur(80px)", pointerEvents: "none", zIndex: 0
            }} />

            <Box sx={{ position: "relative", zIndex: 10 }}>
                <Header />
            </Box>

            <Container 
                maxWidth="md" 
                sx={{ mt: 8, position: "relative", zIndex: 1 }}
                component={motion.div}
                variants={containerVariants}
                initial="hidden"
                animate="visible"
            >
                <motion.div variants={itemVariants}>
                    <Typography variant="h4" sx={{ fontWeight: 800, mb: 1, letterSpacing: "-0.02em" }}>My Profile</Typography>
                    <Typography sx={{ color: "text.secondary", mb: 6, fontSize: "1.1rem" }}>Manage your personal information and account settings.</Typography>
                </motion.div>

                <motion.div variants={itemVariants}>
                    <Card sx={{ 
                        bgcolor: "background.paper", 
                        backdropFilter: "blur(20px)",
                        border: `1px solid ${theme.palette.divider}`, 
                        borderRadius: 4, color: "text.primary",
                        boxShadow: "0 20px 40px -10px rgba(0,0,0,0.3)"
                    }}>
                        <CardContent sx={{ p: { xs: 3, md: 5 } }}>
                            <Box sx={{ display: "flex", alignItems: "center", gap: 4, mb: 5 }}>
                                <Avatar 
                                    src={avatarUrl}
                                    sx={{ 
                                        width: 100, height: 100, 
                                        bgcolor: avatarUrl ? "transparent" : "#8B5CF6",
                                        fontSize: "2.5rem",
                                        border: "4px solid rgba(255,255,255,0.1)" 
                                    }}
                                >
                                    {!avatarUrl && initials}
                                </Avatar>
                                <Box>
                                    <Typography variant="h5" sx={{ fontWeight: 700, mb: 0.5 }}>{fullName}</Typography>
                                    <Typography sx={{ color: "text.secondary", display: "flex", alignItems: "center", gap: 1, mb: 1.5 }}>
                                        <Mail size={16} /> {email}
                                    </Typography>
                                    <Box sx={{ display: "inline-flex", alignItems: "center", gap: 1, px: 1.5, py: 0.5, borderRadius: 2, bgcolor: "rgba(16,185,129,0.1)", color: "#10B981", border: "1px solid rgba(16,185,129,0.2)" }}>
                                        <ShieldCheck size={14} />
                                        <Typography sx={{ fontSize: "0.8rem", fontWeight: 600 }}>Active Account</Typography>
                                    </Box>
                                </Box>
                            </Box>

                            <Divider sx={{ borderColor: "rgba(255,255,255,0.08)", mb: 4 }} />

                            <Grid container spacing={4}>
                                <Grid item xs={12} sm={6}>
                                    <Box sx={{ mb: 3 }}>
                                        <Typography sx={{ color: "text.secondary", fontSize: "0.85rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", mb: 1, display: "flex", alignItems: "center", gap: 1 }}>
                                            <User size={16} /> Full Name
                                        </Typography>
                                        <Typography sx={{ fontSize: "1.1rem", fontWeight: 500 }}>{fullName}</Typography>
                                    </Box>
                                </Grid>
                                <Grid item xs={12} sm={6}>
                                    <Box sx={{ mb: 3 }}>
                                        <Typography sx={{ color: "text.secondary", fontSize: "0.85rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", mb: 1, display: "flex", alignItems: "center", gap: 1 }}>
                                            <Key size={16} /> Auth Provider
                                        </Typography>
                                        <Typography sx={{ fontSize: "1.1rem", fontWeight: 500 }}>{provider}</Typography>
                                    </Box>
                                </Grid>
                                <Grid item xs={12} sm={6}>
                                    <Box sx={{ mb: 3 }}>
                                        <Typography sx={{ color: "text.secondary", fontSize: "0.85rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", mb: 1, display: "flex", alignItems: "center", gap: 1 }}>
                                            <Calendar size={16} /> Member Since
                                        </Typography>
                                        <Typography sx={{ fontSize: "1.1rem", fontWeight: 500 }}>{memberSince}</Typography>
                                    </Box>
                                </Grid>
                                <Grid item xs={12} sm={6}>
                                    <Box sx={{ mb: 3 }}>
                                        <Typography sx={{ color: "text.secondary", fontSize: "0.85rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", mb: 1, display: "flex", alignItems: "center", gap: 1 }}>
                                            <Clock size={16} /> Last Login
                                        </Typography>
                                        <Typography sx={{ fontSize: "1.1rem", fontWeight: 500 }}>{lastLogin}</Typography>
                                    </Box>
                                </Grid>
                            </Grid>
                        </CardContent>
                    </Card>
                </motion.div>
            </Container>
        </Box>
    );
}
