import { useState } from "react";
import { Box, Typography, Button, TextField, Container, Card, CardContent, Divider } from "@mui/material";
import { motion, AnimatePresence } from "framer-motion";
import SpaceBackground from "./Landing/SpaceBackground";
import { useNavigate } from "react-router-dom";
import { Mail, Lock, LogIn, UserPlus } from "lucide-react";
import { supabase } from "../lib/supabase";

export default function Auth() {
    const navigate = useNavigate();
    const [isLogin, setIsLogin] = useState(true);
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);
        
        try {
            if (isLogin) {
                const { error } = await supabase.auth.signInWithPassword({
                    email,
                    password
                });
                if (error) throw error;
            } else {
                const { error } = await supabase.auth.signUp({
                    email,
                    password,
                    options: {
                        data: {
                            full_name: name
                        }
                    }
                });
                if (error) throw error;
            }
            navigate("/dashboard");
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleGoogleAuth = async () => {
        try {
            const { error } = await supabase.auth.signInWithOAuth({
                provider: 'google',
            });
            if (error) throw error;
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <Box sx={{
            position: "relative",
            width: "100%",
            minHeight: "100vh",
            display: "flex",
            bgcolor: "#0B1120",
            color: "white"
        }}>
            {/* Left side ambient background (Hidden on mobile) */}
            <Box sx={{ flex: 1, position: "relative", display: { xs: "none", md: "block" } }}>
                <SpaceBackground />
                <Box sx={{ 
                    position: "absolute", zIndex: 10, p: 8, 
                    display: 'flex', flexDirection: 'column', justifyContent: 'center', height: '100%'
                }}>
                    <Typography variant="h2" sx={{ fontWeight: 800, mb: 3 }}>
                        Unlock Your<br/>Research Potential
                    </Typography>
                    <Typography variant="h6" sx={{ color: "#94A3B8", maxWidth: 400, fontWeight: 400 }}>
                        Join thousands of researchers using AI to navigate scientific literature with unprecedented speed.
                    </Typography>
                </Box>
            </Box>

            {/* Right side form */}
            <Box sx={{ 
                flex: { xs: 1, md: 0.8 }, 
                display: "flex", 
                alignItems: "center", 
                justifyContent: "center",
                p: 4,
                bgcolor: "rgba(11,17,32,0.9)",
                zIndex: 20
            }}>
                <Container maxWidth="sm">
                    <Card sx={{ 
                        bgcolor: "rgba(30,41,59,0.7)", 
                        backdropFilter: "blur(20px)",
                        border: "1px solid rgba(255,255,255,0.1)",
                        borderRadius: 4,
                        boxShadow: "0 25px 50px -12px rgba(0,0,0,0.5)"
                    }}>
                        <CardContent sx={{ p: { xs: 3, sm: 6 } }}>
                            <Box sx={{ display: 'flex', mb: 4, bgcolor: "rgba(0,0,0,0.3)", borderRadius: 2, p: 0.5 }}>
                                <Button 
                                    fullWidth 
                                    onClick={() => setIsLogin(true)}
                                    sx={{ 
                                        py: 1.5, 
                                        borderRadius: 1.5,
                                        bgcolor: isLogin ? "rgba(139,92,246,0.2)" : "transparent",
                                        color: isLogin ? "#A78BFA" : "#64748B",
                                        textTransform: "none",
                                        fontWeight: isLogin ? 600 : 500
                                    }}
                                >
                                    Sign In
                                </Button>
                                <Button 
                                    fullWidth 
                                    onClick={() => setIsLogin(false)}
                                    sx={{ 
                                        py: 1.5, 
                                        borderRadius: 1.5,
                                        bgcolor: !isLogin ? "rgba(139,92,246,0.2)" : "transparent",
                                        color: !isLogin ? "#A78BFA" : "#64748B",
                                        textTransform: "none",
                                        fontWeight: !isLogin ? 600 : 500
                                    }}
                                >
                                    Sign Up
                                </Button>
                            </Box>

                            <Typography variant="h5" sx={{ fontWeight: 700, mb: 1, color: "white" }}>
                                {isLogin ? "Welcome back" : "Create an account"}
                            </Typography>
                            <Typography sx={{ color: "#94A3B8", mb: 4, fontSize: "0.9rem" }}>
                                {isLogin ? "Enter your credentials to access your workspace." : "Start organizing your research library today."}
                            </Typography>
                            
                            {error && (
                                <Box sx={{ mb: 3, p: 1.5, bgcolor: "rgba(239, 68, 68, 0.1)", border: "1px solid rgba(239, 68, 68, 0.2)", borderRadius: 2 }}>
                                    <Typography sx={{ color: "#FCA5A5", fontSize: "0.85rem", textAlign: "center" }}>
                                        {error}
                                    </Typography>
                                </Box>
                            )}

                            <Button 
                                fullWidth
                                onClick={handleGoogleAuth}
                                sx={{
                                    py: 1.5, mb: 3,
                                    bgcolor: "white", color: "#0F172A",
                                    fontWeight: 600, textTransform: "none",
                                    borderRadius: 2,
                                    "&:hover": { bgcolor: "#F8FAFC" }
                                }}
                            >
                                <Box component="img" src="https://fonts.gstatic.com/s/i/productlogos/googleg/v6/24px.svg" sx={{ width: 18, height: 18, mr: 2 }} />
                                Continue with Google
                            </Button>

                            <Divider sx={{ mb: 3, "&::before, &::after": { borderColor: "rgba(255,255,255,0.1)" } }}>
                                <Typography sx={{ color: "#64748B", fontSize: "0.85rem" }}>OR</Typography>
                            </Divider>

                            <form onSubmit={handleSubmit}>
                                <AnimatePresence mode="wait">
                                    {!isLogin && (
                                        <motion.div
                                            initial={{ opacity: 0, height: 0 }}
                                            animate={{ opacity: 1, height: "auto" }}
                                            exit={{ opacity: 0, height: 0 }}
                                        >
                                            <TextField
                                                fullWidth
                                                placeholder="Full Name"
                                                variant="outlined"
                                                value={name}
                                                onChange={(e) => setName(e.target.value)}
                                                sx={{ mb: 3, ...inputStyles }}
                                                required={!isLogin}
                                            />
                                        </motion.div>
                                    )}
                                </AnimatePresence>

                                <TextField
                                    fullWidth
                                    placeholder="Email Address"
                                    type="email"
                                    variant="outlined"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    sx={{ mb: 3, ...inputStyles }}
                                    required
                                />
                                
                                <TextField
                                    fullWidth
                                    placeholder="Password"
                                    type="password"
                                    variant="outlined"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    sx={{ mb: 2, ...inputStyles }}
                                    required
                                />

                                {isLogin && (
                                    <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 3 }}>
                                        <Typography sx={{ color: "#A78BFA", fontSize: "0.85rem", cursor: "pointer", "&:hover": { textDecoration: "underline" } }}>
                                            Forgot Password?
                                        </Typography>
                                    </Box>
                                )}

                                <Button 
                                    fullWidth
                                    type="submit"
                                    sx={{
                                        py: 1.5, mt: isLogin ? 0 : 2,
                                        background: "linear-gradient(135deg, rgba(139,92,246,0.9) 0%, rgba(59,130,246,0.9) 100%)",
                                        color: "white",
                                        fontWeight: 600,
                                        textTransform: "none",
                                        borderRadius: 2,
                                        boxShadow: "0 4px 14px 0 rgba(139,92,246,0.39)",
                                        "&:hover": { background: "linear-gradient(135deg, rgba(139,92,246,1) 0%, rgba(59,130,246,1) 100%)" }
                                    }}
                                >
                                    {loading ? "Please wait..." : isLogin ? "Sign In" : "Create Account"}
                                </Button>
                            </form>
                        </CardContent>
                    </Card>
                </Container>
            </Box>
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
        "&.Mui-focused fieldset": { borderColor: "#A78BFA" }
    },
    "& .MuiInputBase-input::placeholder": { color: "#64748B", opacity: 1 }
};
