import { createTheme } from "@mui/material/styles";

const theme = createTheme({
    palette: {
        mode: "dark",
        primary: {
            main: "#8B5CF6", // Purple accent
            light: "#A78BFA",
            dark: "#7C3AED",
            contrastText: "#FFFFFF",
        },
        secondary: {
            main: "#3B82F6", // Blue accent
            light: "#60A5FA",
            dark: "#2563EB",
            contrastText: "#FFFFFF",
        },
        success: {
            main: "#22C55E",
        },
        warning: {
            main: "#F59E0B",
        },
        background: {
            default: "#0B1120", // Deep background
            paper: "#1E293B",   // Cards
        },
        text: {
            primary: "#F8FAFC",
            secondary: "#94A3B8",
        },
        divider: "rgba(255, 255, 255, 0.08)",
    },
    typography: {
        fontFamily: [
            "Inter",
            "-apple-system",
            "BlinkMacSystemFont",
            "Segoe UI",
            "Roboto",
            "sans-serif"
        ].join(","),
        h1: { fontWeight: 700, letterSpacing: "-0.02em" },
        h2: { fontWeight: 700, letterSpacing: "-0.02em" },
        h3: { fontWeight: 700, letterSpacing: "-0.02em" },
        h4: { fontWeight: 700, letterSpacing: "-0.01em" },
        h5: { fontWeight: 600, letterSpacing: "-0.01em" },
        h6: { fontWeight: 600, letterSpacing: "-0.01em" },
        subtitle1: { fontWeight: 600, letterSpacing: "-0.01em" },
        subtitle2: { fontWeight: 500 },
        button: {
            textTransform: "none",
            fontWeight: 600,
            letterSpacing: "0.01em",
        }
    },
    shape: {
        borderRadius: 16,
    },
    components: {
        MuiPaper: {
            styleOverrides: {
                root: {
                    backgroundImage: "none", // Remove default MUI dark mode elevation overlay
                    boxShadow: "0 10px 30px -10px rgba(0, 0, 0, 0.4)",
                    border: "1px solid rgba(255, 255, 255, 0.05)",
                }
            }
        },
        MuiButton: {
            styleOverrides: {
                root: {
                    borderRadius: 12,
                    padding: "8px 20px",
                    boxShadow: "none",
                    transition: "all 0.2s ease-in-out",
                    "&:hover": {
                        boxShadow: "0 8px 20px -6px rgba(139, 92, 246, 0.4)",
                        transform: "translateY(-1px)",
                    }
                },
                contained: {
                    background: "linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%)",
                },
                outlined: {
                    borderWidth: "1.5px",
                    borderColor: "rgba(255, 255, 255, 0.15)",
                    color: "#F8FAFC",
                    "&:hover": {
                        borderWidth: "1.5px",
                        backgroundColor: "rgba(255, 255, 255, 0.05)",
                    }
                }
            }
        },
        MuiTextField: {
            styleOverrides: {
                root: {
                    "& .MuiOutlinedInput-root": {
                        borderRadius: 12,
                        backgroundColor: "rgba(255, 255, 255, 0.02)",
                        transition: "all 0.2s",
                        "&:hover .MuiOutlinedInput-notchedOutline": {
                            borderColor: "rgba(255, 255, 255, 0.2)",
                        },
                        "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                            borderColor: "#8B5CF6",
                            borderWidth: "1px",
                        },
                        "&.Mui-focused": {
                            backgroundColor: "rgba(139, 92, 246, 0.05)",
                            boxShadow: "0 0 0 4px rgba(139, 92, 246, 0.15)",
                        }
                    }
                }
            }
        },
        MuiChip: {
            styleOverrides: {
                root: {
                    borderRadius: 8,
                    fontWeight: 500,
                },
                filled: {
                    backgroundColor: "rgba(139, 92, 246, 0.15)",
                    color: "#A78BFA",
                    border: "1px solid rgba(139, 92, 246, 0.3)",
                }
            }
        }
    }
});

export default theme;