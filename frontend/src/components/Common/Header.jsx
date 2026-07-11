import {
    AppBar,
    Toolbar,
    Box,
    Typography,
    InputBase,
    Button,
    Avatar,
    IconButton,
    Tooltip,
    Menu,
    MenuItem
} from "@mui/material";
import { useState } from "react";

import { motion } from "framer-motion";
import { 
    BrainCircuit, 
    Search, 
    CloudUpload, 
    Moon, 
    Sun,
    Bell 
} from "lucide-react";
import UserProfileMenu from "./UserProfileMenu";
import { useThemeContext } from "../../contexts/ThemeContext";
import { useTheme } from "@mui/material/styles";

export default function Header({ searchQuery = "", onSearchChange }) {
    const [anchorElNotifications, setAnchorElNotifications] = useState(null);
    const notificationsOpen = Boolean(anchorElNotifications);
    const { mode, toggleTheme } = useThemeContext();
    const theme = useTheme();

    return (
        <AppBar
            position="static"
            elevation={0}
            sx={{
                bgcolor: "transparent",
                borderBottom: "1px solid rgba(255, 255, 255, 0.05)",
                backdropFilter: "blur(20px)",
            }}
        >
            <Toolbar
                sx={{
                    justifyContent: "space-between",
                    minHeight: "72px !important",
                    px: { xs: 2, md: 4 },
                }}
            >
                {/* Logo Section */}
                <Box
                    component={motion.div}
                    whileHover={{ scale: 1.02 }}
                    sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1.5,
                        cursor: "pointer"
                    }}
                >
                    <Box sx={{ 
                        p: 1, 
                        borderRadius: 2, 
                        background: "linear-gradient(135deg, rgba(139,92,246,0.2) 0%, rgba(59,130,246,0.2) 100%)",
                        color: "#8B5CF6",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        border: "1px solid rgba(139,92,246,0.2)"
                    }}>
                        <BrainCircuit size={28} strokeWidth={2.5} />
                    </Box>
                    <Box>
                        <Typography
                            variant="h6"
                            sx={{
                                fontWeight: 700,
                                color: theme.palette.text.primary,
                                lineHeight: 1.2,
                                letterSpacing: "-0.02em"
                            }}
                        >
                            Research Paper
                        </Typography>
                        <Typography
                            variant="body2"
                            sx={{
                                color: theme.palette.primary.main,
                                fontWeight: 600,
                                fontSize: "0.8rem",
                                letterSpacing: "0.05em",
                                textTransform: "uppercase"
                            }}
                        >
                            Intelligence System
                        </Typography>
                    </Box>
                </Box>

                {/* Global Search */}
                <Box
                    sx={{
                        width: { xs: "0%", md: "40%" },
                        display: { xs: "none", md: "flex" },
                        bgcolor: "rgba(255, 255, 255, 0.03)",
                        borderRadius: "12px",
                        px: 2,
                        py: 0.75,
                        alignItems: "center",
                        border: "1px solid rgba(255, 255, 255, 0.08)",
                        transition: "all 0.2s ease",
                        "&:hover": {
                            bgcolor: "rgba(255, 255, 255, 0.05)",
                            borderColor: "rgba(255, 255, 255, 0.15)",
                        },
                        "&:focus-within": {
                            bgcolor: "rgba(255, 255, 255, 0.06)",
                            borderColor: "#3B82F6",
                            boxShadow: "0 0 0 3px rgba(59,130,246,0.15)"
                        }
                    }}
                >
                    <Search size={18} color={theme.palette.text.secondary} style={{ marginRight: 8 }} />
                    <InputBase
                        placeholder="Search papers, authors, methodologies..."
                        value={searchQuery}
                        onChange={(e) => onSearchChange && onSearchChange(e.target.value)}
                        sx={{
                            color: theme.palette.text.primary,
                            width: "100%",
                            fontSize: "0.95rem",
                            "& input::placeholder": {
                                color: theme.palette.text.secondary,
                                opacity: 1,
                            }
                        }}
                    />
                </Box>

                {/* Right Actions */}
                <Box
                    sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 2
                    }}
                >
                    <Tooltip title={`Switch to ${mode === 'dark' ? 'Light' : 'Dark'} Mode`}>
                        <IconButton 
                            onClick={toggleTheme}
                            sx={{ 
                                color: theme.palette.text.secondary, 
                                "&:hover": { color: theme.palette.text.primary, bgcolor: "rgba(139,92,246,0.1)" }
                            }}
                        >
                            {mode === 'dark' ? <Moon size={20} /> : <Sun size={20} />}
                        </IconButton>
                    </Tooltip>

                    <Tooltip title="Notifications (Coming Soon)">
                        <IconButton 
                            onClick={(e) => setAnchorElNotifications(e.currentTarget)}
                            sx={{ 
                                color: theme.palette.text.secondary,
                                "&:hover": { color: theme.palette.text.primary, bgcolor: mode === 'dark' ? "rgba(255,255,255,0.05)" : "rgba(0,0,0,0.05)" }
                            }}
                        >
                            <Bell size={20} />
                        </IconButton>
                    </Tooltip>
                    <Menu
                        anchorEl={anchorElNotifications}
                        open={notificationsOpen}
                        onClose={() => setAnchorElNotifications(null)}
                        PaperProps={{
                            elevation: 0,
                            sx: {
                                mt: 1.5,
                                bgcolor: "rgba(30, 41, 59, 0.95)",
                                backdropFilter: "blur(16px)",
                                border: "1px solid rgba(255, 255, 255, 0.1)",
                                color: "#94A3B8",
                                minWidth: 200,
                            }
                        }}
                        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                    >
                        <MenuItem disabled sx={{ py: 2, justifyContent: 'center', opacity: "1 !important" }}>
                            No notifications yet.
                        </MenuItem>
                    </Menu>

                    <Button
                        variant="contained"
                        startIcon={<CloudUpload size={18} />}
                        onClick={() => window.dispatchEvent(new CustomEvent('open-upload'))}
                        sx={{
                            display: { xs: "none", sm: "flex" },
                            ml: 1
                        }}
                    >
                        Upload PDF
                    </Button>

                    <UserProfileMenu />
                </Box>
            </Toolbar>
        </AppBar>
    );
}