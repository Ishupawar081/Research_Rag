import { useState } from "react";
import { Box, Typography, Avatar, Menu, MenuItem, Divider, ListItemIcon } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { User, Settings, LogOut, Library, HelpCircle } from "lucide-react";
import { useTheme } from "@mui/material/styles";

export default function UserProfileMenu() {
    const { user, signOut } = useAuth();
    const theme = useTheme();
    const navigate = useNavigate();
    const [anchorEl, setAnchorEl] = useState(null);
    const open = Boolean(anchorEl);

    if (!user) return null;

    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const handleSignOut = async () => {
        handleClose();
        await signOut();
        navigate("/");
    };

    // Extract user info
    const fullName = user.user_metadata?.full_name || user.email?.split('@')[0] || "Researcher";
    const email = user.email || "";
    const avatarUrl = user.user_metadata?.avatar_url || "";
    const initials = fullName.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();

    return (
        <Box>
            <Avatar
                onClick={handleClick}
                src={avatarUrl}
                alt={fullName}
                sx={{
                    width: 40,
                    height: 40,
                    cursor: "pointer",
                    bgcolor: avatarUrl ? "transparent" : theme.palette.primary.main,
                    border: `2px solid ${theme.palette.divider}`,
                    transition: "all 0.2s ease",
                    "&:hover": {
                        borderColor: theme.palette.primary.light,
                        transform: "scale(1.05)"
                    }
                }}
            >
                {!avatarUrl && initials}
            </Avatar>

            <Menu
                anchorEl={anchorEl}
                open={open}
                onClose={handleClose}
                onClick={handleClose}
                PaperProps={{
                    elevation: 0,
                    sx: {
                        overflow: 'visible',
                        filter: 'drop-shadow(0px 10px 30px rgba(0,0,0,0.5))',
                        mt: 1.5,
                        bgcolor: theme.palette.background.paper,
                        backdropFilter: "blur(16px)",
                        border: `1px solid ${theme.palette.divider}`,
                        color: theme.palette.text.primary,
                        minWidth: 220,
                        '& .MuiAvatar-root': {
                            width: 32,
                            height: 32,
                            ml: -0.5,
                            mr: 1,
                        },
                        '&:before': {
                            content: '""',
                            display: 'block',
                            position: 'absolute',
                            top: 0,
                            right: 14,
                            width: 10,
                            height: 10,
                            bgcolor: theme.palette.background.paper,
                            transform: 'translateY(-50%) rotate(45deg)',
                            zIndex: 0,
                            borderTop: `1px solid ${theme.palette.divider}`,
                            borderLeft: `1px solid ${theme.palette.divider}`,
                        },
                    },
                }}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
                <Box sx={{ px: 2, py: 1.5 }}>
                    <Typography sx={{ fontWeight: 600, color: theme.palette.text.primary, fontSize: "0.95rem" }}>
                        {fullName}
                    </Typography>
                    <Typography sx={{ color: theme.palette.text.secondary, fontSize: "0.8rem", mt: 0.5 }}>
                        {email}
                    </Typography>
                </Box>
                <Divider sx={{ borderColor: theme.palette.divider }} />
                
                <MenuItem onClick={() => { handleClose(); navigate("/profile"); }} sx={{ py: 1.5, "&:hover": { bgcolor: "rgba(139,92,246,0.05)" } }}>
                    <ListItemIcon sx={{ color: theme.palette.primary.main }}>
                        <User size={18} />
                    </ListItemIcon>
                    My Profile
                </MenuItem>
                
                <MenuItem onClick={() => { handleClose(); navigate("/dashboard"); }} sx={{ py: 1.5, "&:hover": { bgcolor: "rgba(139,92,246,0.05)" } }}>
                    <ListItemIcon sx={{ color: theme.palette.primary.main }}>
                        <Library size={18} />
                    </ListItemIcon>
                    My Papers
                </MenuItem>
                
                <MenuItem onClick={() => { handleClose(); navigate("/settings"); }} sx={{ py: 1.5, "&:hover": { bgcolor: "rgba(139,92,246,0.05)" } }}>
                    <ListItemIcon sx={{ color: theme.palette.primary.main }}>
                        <Settings size={18} />
                    </ListItemIcon>
                    Settings
                </MenuItem>
                
                <MenuItem onClick={handleClose} sx={{ py: 1.5, "&:hover": { bgcolor: "rgba(139,92,246,0.05)" } }}>
                    <ListItemIcon sx={{ color: theme.palette.primary.main }}>
                        <HelpCircle size={18} />
                    </ListItemIcon>
                    Help & Support
                </MenuItem>
                
                <Divider sx={{ borderColor: theme.palette.divider }} />
                
                <MenuItem onClick={handleSignOut} sx={{ py: 1.5, color: theme.palette.error?.main || "#FCA5A5", "&:hover": { bgcolor: "rgba(239, 68, 68, 0.1)" } }}>
                    <ListItemIcon sx={{ color: theme.palette.error?.main || "#FCA5A5" }}>
                        <LogOut size={18} />
                    </ListItemIcon>
                    Sign Out
                </MenuItem>
            </Menu>
        </Box>
    );
}
