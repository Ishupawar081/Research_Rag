import React, { createContext, useContext, useState, useMemo, useEffect } from 'react';
import { createTheme, ThemeProvider as MUIThemeProvider } from '@mui/material/styles';
import CssBaseline from "@mui/material/CssBaseline";

const ThemeContext = createContext({
    toggleTheme: () => {},
    mode: 'dark'
});

export const useThemeContext = () => useContext(ThemeContext);

export function ThemeProvider({ children }) {
    const [mode, setMode] = useState(() => {
        const saved = localStorage.getItem('themeMode');
        return saved ? saved : 'dark';
    });

    useEffect(() => {
        localStorage.setItem('themeMode', mode);
    }, [mode]);

    const toggleTheme = () => {
        setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
    };

    const theme = useMemo(
        () =>
            createTheme({
                palette: {
                    mode,
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
                    success: { main: "#22C55E" },
                    warning: { main: "#F59E0B" },
                    background: {
                        default: mode === 'dark' ? "#0B1120" : "#F1F5F9",
                        paper: mode === 'dark' ? "#1E293B" : "#FFFFFF",
                    },
                    text: {
                        primary: mode === 'dark' ? "#F8FAFC" : "#0F172A",
                        secondary: mode === 'dark' ? "#94A3B8" : "#475569",
                    },
                    divider: mode === 'dark' ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.08)",
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
                                backgroundImage: "none", 
                                boxShadow: mode === 'dark' 
                                    ? "0 10px 30px -10px rgba(0, 0, 0, 0.4)" 
                                    : "0 10px 30px -10px rgba(0, 0, 0, 0.05)",
                                border: mode === 'dark' 
                                    ? "1px solid rgba(255, 255, 255, 0.05)"
                                    : "1px solid rgba(0, 0, 0, 0.05)",
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
                                color: "#FFFFFF",
                            },
                            outlined: {
                                borderWidth: "1.5px",
                                borderColor: mode === 'dark' ? "rgba(255, 255, 255, 0.15)" : "rgba(0, 0, 0, 0.15)",
                                color: mode === 'dark' ? "#F8FAFC" : "#0F172A",
                                "&:hover": {
                                    borderWidth: "1.5px",
                                    backgroundColor: mode === 'dark' ? "rgba(255, 255, 255, 0.05)" : "rgba(0, 0, 0, 0.05)",
                                }
                            }
                        }
                    },
                    MuiTextField: {
                        styleOverrides: {
                            root: {
                                "& .MuiOutlinedInput-root": {
                                    borderRadius: 12,
                                    backgroundColor: mode === 'dark' ? "rgba(255, 255, 255, 0.02)" : "rgba(0, 0, 0, 0.02)",
                                    transition: "all 0.2s",
                                    "&:hover .MuiOutlinedInput-notchedOutline": {
                                        borderColor: mode === 'dark' ? "rgba(255, 255, 255, 0.2)" : "rgba(0, 0, 0, 0.2)",
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
                                color: "#8B5CF6", // Adjust slightly for light mode contrast
                                border: "1px solid rgba(139, 92, 246, 0.3)",
                            }
                        }
                    }
                }
            }),
        [mode],
    );

    return (
        <ThemeContext.Provider value={{ toggleTheme, mode }}>
            <MUIThemeProvider theme={theme}>
                <CssBaseline />
                {children}
            </MUIThemeProvider>
        </ThemeContext.Provider>
    );
}
